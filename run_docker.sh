#!/bin/bash

user=$(whoami)
user_id=$(id -u)
port=$((8000 + user_id))
app_name=wann-app-$user
container_id=$(docker ps -a | grep "${app_name}" | awk -F'  ' '{print $1}')
status=$(docker ps -a | grep "${container_id}" | awk -F'  ' '{print $5}')
echo "User: $user, using port: $port"

function start() {
	if [[ -z "$container_id" ]]; then
		docker run -d -p "$port":8050 -v "$HOME":/data --name "$app_name" wannier-app:0.9 >/dev/null
		echo "A docker container named $app_name was created."
	else
		if [[ $status =~ "Exited" ]]; then
			docker start "$container_id"
			echo "Container $app_name has been started."
		else
			echo "Container $app_name is already running."
		fi
	fi
}

function stop() {
	if [[ $status =~ "Up" ]]; then
		docker stop "$container_id" >/dev/null
		echo "Container $app_name has been stopped."
	else
		echo "Container $app_name is not running."
	fi
}

if [[ $1 == "start" ]]; then
	start
elif [[ $1 == "stop" ]]; then
	stop
fi
