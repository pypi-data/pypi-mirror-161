import json
import aicmder as cmder


if __name__ == "__main__":    
    with open("config.json") as json_f:
        config = json.load(json_f)
        # print(config)
        exec_cmd = ['-w', config["w"], '-c', json.dumps(config["config"]),
                   '-p', config["port"], '--max_connect', config["max_conn"], '--device_map']
        exec_cmd.extend(config["device"])
        print(exec_cmd)
        serve = cmder.serve.ServeCommand()
        serve.execute(exec_cmd)