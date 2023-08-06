import json
import itertools
from typing import List
from pathlib import Path
import yaml

from ..docker import DockerBuilder
from .lib import (
    load_config,
    compile_config,
    create_routing_table,
)


def get_port(ports):
    if isinstance(ports, str):
        return int(ports.split(":")[-1])
    elif isinstance(ports, list):
        return [int(port.split(":")[-1]) for port in ports]
    elif isinstance(ports, dict):
        return {key: int(value.split(":")[-1]) for key, value in ports.items()}
    else:
        raise TypeError(f"unexpected type {type(ports)}")


def get_container_ports(routing_table_n):
    ports = []
    for key, port in routing_table_n.items():
        key = key.replace("_", "-")[:5]
        if isinstance(port, str):
            ports.append({"containerPort": get_port(port), "name": key})
        elif isinstance(port, list):
            for i, p in enumerate(port):
                ports.append({"containerPort": get_port(p), "name": f"{key}-{i}"})
        elif isinstance(port, dict):
            for k, v in port.items():
                k = k.replace("_", "-")[:9]
                ports.append({"containerPort": get_port(v), "name": f"{key}-{k}"})
        else:
            raise TypeError(f"unexpected type {type(ports)}")
    return ports


def get_service_ports(routing_table_n):
    ports = []
    for key, port in routing_table_n.items():
        key = key.replace("_", "-")[:5]
        if isinstance(port, str):
            ports.append(
                {
                    "port": get_port(port),
                    "targetPort": key,
                    "protocol": "TCP",
                    "name": key,
                }
            )
        elif isinstance(port, list):
            for i, p in enumerate(port):
                ports.append(
                    {
                        "port": get_port(p),
                        "targetPort": f"{key}-{i}",
                        "protocol": "TCP",
                        "name": f"{key}-{i}",
                    }
                )
        elif isinstance(port, dict):
            for k, v in port.items():
                k = k.replace("_", "-")[:9]
                ports.append(
                    {
                        "port": get_port(v),
                        "targetPort": f"{key}-{k}",
                        "protocol": "TCP",
                        "name": f"{key}-{k}",
                    }
                )
        else:
            raise TypeError(f"unexpected type {type(ports)}")
    return ports


def create_mysql_database_k8s_dicts():
    db_yaml = """
apiVersion: v1
kind: Service
metadata:
  name: mysql
spec:
  ports:
  - port: 3306
  selector:
    app: mysql
  clusterIP: None
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
spec:
  selector:
    matchLabels:
      app: mysql
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - image: mysql:8.0
        name: mysql
        env:
        - name: MYSQL_ROOT_PASSWORD
          value: password
        ports:
        - containerPort: 3306
          name: mysql
        volumeMounts:
        - name: mysql-persistent-storage
          mountPath: /var/lib/mysql
        args: ["--sql-mode="]
      volumes:
      - name: mysql-persistent-storage
        persistentVolumeClaim:
          claimName: mysql-pv-claim
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mysql-pv-volume
  labels:
    type: local
spec:
  storageClassName: manual
  capacity:
    storage: 20Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/mnt/data"
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pv-claim
spec:
  storageClassName: manual
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
"""
    return yaml.load_all(db_yaml, yaml.FullLoader)


def create_k8s_dicts(config, routing_table, image_name, port):
    dicts = []

    for n, info in config.items():
        n = n.replace("_", "-")
        kwargs = {
            **info,
            **routing_table[n],
            "is_respawned": False,
            "database_addr": "mysql://root:password@mysql.default.svc.cluster.local/mydb",  # noqa: E501
            "root_dir": ".",
        }
        args = list(
            itertools.chain.from_iterable(
                [f"--{key}", f"{json.dumps(value)}"] for key, value in kwargs.items()
            )
        )
        ports = get_container_ports(routing_table[n])
        dicts.append(
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {"name": n},
                "spec": {
                    # 'replicas': 3,
                    "selector": {"matchLabels": {"app": n}},
                    "template": {
                        "metadata": {"labels": {"app": n}},
                        "spec": {
                            "containers": [
                                {
                                    "name": n,
                                    "imagePullPolicy": "Always",
                                    "image": image_name,
                                    "args": [f"run-{info['type'].replace('_', '-')}"]
                                    + args,
                                    "ports": ports,
                                    "stdin": True,
                                    "tty": True,
                                }
                            ]
                            # "initContainers": []
                        },
                    },
                },
            }
        )
        ports = get_service_ports(routing_table[n])
        dicts.append(
            {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": f"service-{n}",
                    "labels": {
                        "app": n,
                    },
                },
                "spec": {"ports": ports, "selector": {"app": n}},
            }
        )

    # dicts.append({
    #     'apiVersion': 'networking.k8s.io/v1',
    #     'kind': 'Ingress',
    #     'metadata': {
    #         'name': 'ingress',
    #         'annotations': {
    #             'nginx.ingress.kubernetes.io/rewrite-target': '/'
    #         }
    #     }
    #     'spec':
    #       'ingressClassName': 'nginx-example',
    #       'rules':
    #       - http:
    #           paths:
    #           - path: /testpath
    #             pathType: Prefix
    #             backend:
    #               service:
    #                 name: test
    #                 port:
    #                   number: 80
    dicts.extend(create_mysql_database_k8s_dicts())
    return dicts


def write_yamls(root_dir: Path, dicts: List[dict]):
    yaml.Dumper.ignore_aliases = lambda *args: True
    with open(root_dir / "greap.yaml", "w") as f:
        for d in dicts:
            yaml.dump(d, f, default_flow_style=False)
            f.write("---\n")


def spawn(root_dir: str, default_log_level: str, backtest: bool, port: int):
    docker_builder = DockerBuilder(root_dir).login().build(True).push()
    # docker_builder = DockerBuilder(root_dir).login()
    root_dir = Path(root_dir)
    config = load_config(root_dir)
    config, timer_args = compile_config(
        root_dir, config, backtest, default_log_level, port
    )

    from .address_pool import K8AddressPool

    pool = K8AddressPool()
    routing_table = create_routing_table(root_dir, config, pool)
    dicts = create_k8s_dicts(
        config,
        routing_table,
        f"{docker_builder.repo}:{docker_builder._tag}",
        port,
    )
    write_yamls(root_dir, dicts)
