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
	path, ok := os.LookupEnv("VERSION")
	if !ok {
		glog.Error("VERSION is not defined")
	}
	fmt.Println("VERSION = " + path)
	flag.Set("v", "0")
	flag.Set("alsologtostderr", "true")
	glog.Info("Starting http server...")
	http.HandleFunc("/", rootHandler)
	err := http.ListenAndServe(":5080", nil)
	mux := http.NewServeMux()
	mux.HandleFunc("/", rootHandler)
	mux.HandleFunc("/healthz", healthz)
	if err != nil {
		glog.Error(err)
	}
}

func healthz(w http.ResponseWriter, r *http.Request) {
	ip := r.RemoteAddr
	glog.Info("Request from ip address = " + ip)
	for k, v := range r.Header {
		// Q1: Unable to set response header
		io.WriteString(w, fmt.Sprintf("%s=%s\n", k, v))
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
	w.WriteHeader(http.StatusOK)
	glog.Info("Response code = " + string(http.StatusOK))
}

func rootHandler(w http.ResponseWriter, r *http.Request) {
	ip := r.RemoteAddr
	glog.Info("Request from ip address = " + ip)
	for k, v := range r.Header {
		io.WriteString(w, fmt.Sprintf("%s=%s\n", k, v))
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
	w.WriteHeader(http.StatusOK)
	glog.Info("Response code = " + string(http.StatusOK))
}
