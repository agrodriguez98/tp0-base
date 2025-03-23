package common

import (
	"bufio"
	"fmt"
	"net"
	"time"
	"os"
	"os/signal"
  "syscall"
	"encoding/binary"
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

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	gracefulShutdown := make(chan os.Signal, 1)
	signal.Notify(gracefulShutdown, syscall.SIGTERM)
	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed
	for msgID := 1; msgID <= c.config.LoopAmount; msgID++ {
		select {
		case <-gracefulShutdown:
			c.Shutdown()
		default:
			// Create the connection the server in every loop iteration. Send an
			c.createClientSocket()

			// TODO: Modify the send to avoid short-write
			fmt.Fprintf(
				c.conn,
				"[CLIENT %v] Message N°%v\n",
				c.config.ID,
				msgID,
			)
			msg, err := bufio.NewReader(c.conn).ReadString('\n')
			c.conn.Close()

			if err != nil {
				log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
					c.config.ID,
					err,
				)
				return
			}

			log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
				c.config.ID,
				msg,
			)

			// Wait a time between sending one message and the next one
			time.Sleep(c.config.LoopPeriod)
		}

	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}

func (c *Client) SendBet(b Bet) {
	gracefulShutdown := make(chan os.Signal, 1)
	signal.Notify(gracefulShutdown, syscall.SIGTERM)
	for i := 0; i < 1; i++ {
		select {
		case <-gracefulShutdown:
			c.Shutdown()
		default:
			c.createClientSocket()

			data := fmt.Sprintf(
				"%v|%s|%s|%d|%s|%d",
				c.config.ID,
				b.Name,
				b.LastName,
				b.Document,
				b.Birthdate,
				b.Number,
			)
			size := int32(len(data))

			err1 := binary.Write(c.conn, binary.BigEndian, size)
			if err1 != nil {
				log.Errorf("action: send_size | result: fail | client_id: %v | error: %v",
					c.config.ID,
					err1,
				)
				return
			}

			for c.send(data) < size {
				c.send(data)
			}

			_, err2 := bufio.NewReader(c.conn).ReadString('\n')
			c.conn.Close()

			if err2 != nil {
				log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
					c.config.ID,
					err2,
				)
				return
			}

			log.Infof("action: apuesta_enviada | result: success | dni: %d | numero: %d",
				b.Document,
				b.Number,
			)
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

func (c* Client) Shutdown() {
	c.conn.Close()
	log.Infof("action: shutdown | result: success | client_id: %v", c.config.ID)
	os.Exit(0)
}
