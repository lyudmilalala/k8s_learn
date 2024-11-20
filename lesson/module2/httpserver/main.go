package main

import (
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"

	"github.com/golang/glog"
)

func main() {
	flag.Set("v", "0")
	flag.Set("alsologtostderr", "true")
	glog.Info("Starting http server...")
	http.HandleFunc("/healthz", healthz)
	err := http.ListenAndServe(":5080", nil)
	if err != nil {
		glog.Error(err)
	}
}

func healthz(w http.ResponseWriter, r *http.Request) {
	ip := r.RemoteAddr
	glog.Info("Request from ip address = " + ip)
	path, ok := os.LookupEnv("VERSION")
	if !ok {
		glog.Error("VERSION is not defined")
	} else {
		glog.Info("VERSION = " + path)
		w.Header().Set("version", path)
	}
	for k, v := range r.Header {
		// if io.WriteString() before w.Header().Set() then setting headers not work
		// call fmt.Println() before w.Header().Set() will not really affect it
		w.Header().Set(k, v[0])
		w.Header().Set("app", "mila-app")
	}

	io.WriteString(w, "200\n")
	user := r.URL.Query().Get("user")
	if user != "" {
		io.WriteString(w, fmt.Sprintf("hello [%s]\n", user))
	} else {
		io.WriteString(w, "hello [stranger]\n")
	}
	// Q2: show result
	// http: superfluous response.WriteHeader call from main.rootHandler (main.go:66)
	// but did not call two times of WriteHeader
	// w.WriteHeader(http.StatusOK)
	glog.Info("Response code = ", http.StatusOK)
}
