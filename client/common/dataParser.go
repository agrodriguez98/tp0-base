package common

import (
	"fmt"
	"os"
	"encoding/csv"
  "io"
)

type DataParser struct {
  FilePath string
  ChunkSize int
}

func (parser *DataParser) ParseData(c *Client) {
  file, err := os.Open(parser.FilePath)
	if err != nil {
    log.Criticalf(
			"action: open file | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
  defer file.Close()

  csvReader := csv.NewReader(file)
  var records [][]string
	for {
		record, err := csvReader.Read()
    if err == io.EOF {
      if len(records) > 0 {
        data := parser.formatData(c, records)
        // send data
        log.Infof(data)
      }
      break
		}
    if err != nil {
      log.Criticalf(
  			"action: parse file | result: fail | client_id: %v | error: %v",
  			c.config.ID,
  			err,
  		)
		}
		records = append(records, record)
    if len(records) == parser.ChunkSize {
      data := parser.formatData(c, records)
      // send data
      log.Infof(data)
      records = nil
    }
	}
}

func (parser *DataParser) formatData(c *Client, records[][] string) string {
  var data string
	for j := 0; j < len(records); j++ {
		record := fmt.Sprintf(
			"%v|%s|%s|%s|%s|%s",
      c.config.ID,
			records[j][0],
			records[j][1],
			records[j][2],
			records[j][3],
			records[j][4],
		)
		if j == 0 {
			data = data + record
		} else {
			data = data + "||" + record
		}
	}
  return data
}
