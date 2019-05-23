rabbitmqctl add_user worker 123
rabbitmqctl add_vhost worker
rabbitmqctl set_user_tags worker worker_tag
rabbitmqctl set_permissions -p worker worker ".*" ".*" ".*"
