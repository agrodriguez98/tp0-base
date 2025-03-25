package common

import (
	"fmt"
	"strings"
	"bufio"
	"net"
	"time"
	"os"
	"os/signal"
  "syscall"
	"io"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
}

type Bet struct {
	Name					string
	LastName			string
	Document			int
	Birthdate			string
	Number				int
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

func (c *Client) Bets(parser DataParser) {
	c.createClientSocket()
	parser.ParseData(c)
	c.send_done()
	c.recv_send_id()
	c.recv_results()
	c.conn.Close()
	time.Sleep(1 * time.Second)
}

func (c* Client) processResults(data string) []string {
	if data == "\n" {
		var arr []string
		return arr
	}
	return strings.Split(strings.TrimRight(data, "\n"), "|")
}

func (c* Client) recv_results() {
	data, err := bufio.NewReader(c.conn).ReadString('\n')
	if err != nil {
		log.Errorf("action: receive_results | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	winners := c.processResults(data)
	log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %v", len(winners))
}

func (c *Client) SendBets(data string, num_bets int) {
	gracefulShutdown := make(chan os.Signal, 1)
	signal.Notify(gracefulShutdown, syscall.SIGTERM)
	for i := 0; i < 1; i++ {
		select {
		case <-gracefulShutdown:
			c.Shutdown()
		default:
			size := int32(len(data))
			size_packet := fmt.Sprintf("s|%d", size)
			c.send(size_packet)
			c.recv_ack()
			c.send(data)
			c.recv_ack()
			/*log.Infof("action: apuesta_enviada | result: success | cantidad: %d",
				num_bets,
			)*/
		}
	}
}

func (c* Client) send(data string) int32 {
	n, err := io.WriteString(c.conn, data)
	if err != nil {
		log.Errorf("action: send_data | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	return int32(n)
}

func (c* Client) send_done() {
	done_packet := "d|"
	c.send(done_packet)
}

func (c* Client) recv_ack() {
	_, err := bufio.NewReader(c.conn).ReadString('\n')

	if err != nil {
		log.Errorf("action: receive_ack | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
}

func (c* Client) recv_send_id() {
	data, err := bufio.NewReader(c.conn).ReadString('\n')

	if err != nil {
		log.Errorf("action: receive_id | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	if data == "ID\n" {
		c.send(c.config.ID)
	}
}

func (c* Client) Shutdown() {
	c.conn.Close()
	log.Infof("action: shutdown | result: success | client_id: %v", c.config.ID)
	os.Exit(0)
}
