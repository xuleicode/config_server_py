#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 {start|stop|restart|status}"
    exit 1
fi

function start_uranus_tools_server() {
    # Check if the server is already running
    pid=$(ps -ef | grep python3 | grep main_app.py | awk '{print $2}')
    if [ -n "$pid" ]; then
        echo "Warning: main_app.py is already running with PID $pid. Not starting."
        return 0
    fi

    uranus_server_dir=/opt/uranus_tools
    cd $uranus_server_dir
    echo `date` >> $uranus_server_dir/logs/start.log
    python3 main_app.py
}

function stop_uranus_tools_server() {
    pid=$(ps -ef | grep python3 | grep main_app.py | awk '{print $2}')
    if [ -n "$pid" ]; then
        echo "Warning: main_app.py is already running with PID $pid. Killing it..."
        kill -9 $pid
    fi
}

case "$1" in
    start)
        echo "Starting uranus_tools server..."
        start_uranus_tools_server
        ;;
    stop)
        echo "Stopping uranus_tools server..."
        stop_uranus_tools_server
        ;;
    restart)
        echo "Restarting uranus_tools server..."
        stop_uranus_tools_server
        start_uranus_tools_server
        ;;
    status)
        echo "Checking uranus_tools server status..."
        pid=$(ps -ef | grep python3 | grep main_app.py | awk '{print $2}')
        if [ -n "$pid" ]; then
            echo "main_app.py is running with PID $pid."
        else
            echo "main_app.py is not running."
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac





