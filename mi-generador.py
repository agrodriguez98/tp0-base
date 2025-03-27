import sys
import yaml

output_file = sys.argv[1]
num_clients = int(sys.argv[2])

data = dict(
	name = 'tp0',
	services = dict(
		server = dict(
			container_name = 'server',
			image = 'server:latest',
			entrypoint = 'python3 /main.py',
			environment = ['PYTHONUNBUFFERED=1'],
			networks = ['testing_net'],
			volumes = ['./server/config.ini:/config.ini']
		),
		echo_tester = dict(
			container_name = 'echo_tester',
			depends_on = ['server'],
			entrypoint = "sh validar-echo-server.sh",
			image = 'alpine:latest',
			networks = ['testing_net'],
			volumes = ['./validar-echo-server.sh:/validar-echo-server.sh']
		)
	),
	networks = dict(
		testing_net = dict(
			ipam = dict(
				driver = 'default',
				config = [dict(subnet = '172.25.125.0/24')]
			)
		)
	)
)

for i in range(1, num_clients + 1):
    data['services'][f'client{i}'] = dict(
        container_name = f'client{i}',
        image = 'client:latest',
        entrypoint = '/client',
        environment = [f'CLI_ID={i}'],
        networks = ['testing_net'],
        depends_on = ['server'],
		volumes = ['./client/config.yaml:/config.yaml']
    )

with open(output_file, 'w') as file:
	yaml.dump(data, file, default_flow_style=False)
