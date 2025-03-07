// Health check API
package main

import (
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"time"
)

func main() {
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		n := rand.Intn(10)
		if n%2 == 0 {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		} else if n == 3 {
			log.Println("Sleeping for 4 seconds")
			time.Sleep(4 * time.Second)
			fmt.Fprintf(w, "%s", `{"status": "ok", "code": 200, "checks": {"postgres": "up"}}`)
		} else if n == 5 {
			fmt.Fprintf(w, "%s", `{"status": "ok", "code": 200, "checks": {"postgres": "down"}}`)
		} else {
			fmt.Fprintf(w, "%s", `{"status": "ok", "code": 200, "checks": {"postgres": "up"}}`)
		}

	})
	http.ListenAndServe(":8080", nil)
}
