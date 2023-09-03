package main

import (
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"

	"github.com/golang/glog"
)

var start = time.Now()

func main() {
	port, ok := os.LookupEnv("APP_PORT")
	app_port := ":5080"
	if ok {
		app_port = ":" + port
	}
	tmp_log_level, ok := os.LookupEnv("APP_LOG_LEVEL")
	log_level := "1"
	if ok {
		log_level = tmp_log_level
	}
	flag.Set("logtostderr", "true")
	flag.Set("stderrthreshold", log_level) // this not work
	glog.Info("APP_PORT = " + app_port)
	glog.Info("APP_LOG_LEVEL = " + log_level)
	glog.Info("Starting http server...")
	glog.Warning("This is a warning message.")
	http.HandleFunc("/healthz", healthz)
	http.HandleFunc("/greeting", greeting)
	err := http.ListenAndServe(app_port, nil)
	if err != nil {
		fmt.Println(err)
	}
}

func healthz(w http.ResponseWriter, r *http.Request) {
	ip := r.RemoteAddr
	glog.Info("Health check from ip address = " + ip)
	version, ok := os.LookupEnv("VERSION")
	if !ok {
		glog.Warning("VERSION is not defined")
	} else {
		glog.Info("VERSION = " + version)
		w.Header().Set("version", version)
	}
	var livenessTest = false
	livenessTestMark, ok := os.LookupEnv("APP_LIVENESS_TEST")
	if ok {
		livenessTest = livenessTestMark == "Y"
	}
	glog.Info("APP_LIVENESS_TEST = ", livenessTest)
	if livenessTest {
		duration := time.Now().Sub(start)
		msg := fmt.Sprintf("duration = %fs\n", duration.Seconds())
		if duration.Seconds() > 60 {
			w.WriteHeader(500)
			io.WriteString(w, "error: "+msg)
		} else {
			w.WriteHeader(200)
			io.WriteString(w, "pass: "+msg)
		}
	} else {
		w.Header().Set("app", "mila-app")
		io.WriteString(w, "200\n")
	}
}

func greeting(w http.ResponseWriter, r *http.Request) {
	ip := r.RemoteAddr
	glog.Info("Request from ip address = " + ip)
	version, ok := os.LookupEnv("VERSION")
	if !ok {
		glog.Warning("VERSION is not defined")
	} else {
		glog.Info("VERSION = " + version)
		w.Header().Set("version", version)
	}
	for k, v := range r.Header {
		// if io.WriteString() before w.Header().Set() then setting headers not work
		// call fmt.Println() before w.Header().Set() will not really affect it
		w.Header().Set(k, v[0])
		w.Header().Set("app", "mila-app")
	}

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
	// fmt.Println("Response code = ", http.StatusOK)
}
