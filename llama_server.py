'''
서버 기동해보기
'''
import subprocess
import time
import requests
import os

class LlamaServer:
    def __init__(
        self,
        port: int = 8080,
        use_gpu: bool = True
    ):
        self.llama_cpp_repo_path = "./submodules/llama.cpp/llama-server"
        # self.model_path = "./model/llama-3-neural-chat-v1-8b-Q4_K_M.gguf"
        self.model_path = "./model/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
        self.context_length = 8192

        self.port = port
        self.process: subprocess.Popen | None = None
        self.use_gpu = use_gpu

        self.command = (
            [self.llama_cpp_repo_path, "--model"]
            + [self.model_path]
            + ["--ctx-size", str(self.context_length)]
            + ["--port", str(port)]
        )
        if self.use_gpu:
            self.command += [
                "--n-gpu-layers",
                "1000",
            ]  # More than we would ever need, just to be sure.

        print(f"Command to start the server: {self.command}")

    @property
    def base_url(self):
        return f"http://localhost:{self.port}"

    @property
    def completion_url(self):
        return f"{self.base_url}/completion"

    @property
    def health_check_url(self):
        return f"{self.base_url}/health"

    def start(self):
        print(f"Starting the server by executing command {self.command=}")
        self.process = subprocess.Popen(
            self.command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )

        if not self.is_running():
            self.stop()
            raise RuntimeError("Failed to startup! Check the error log messages")

    def is_running(
        self,
        max_connection_attempts: int = 10,
        sleep_time_between_attempts: float = 0.01,
        max_wait_time_for_model_loading: float = 60.0,
    ) -> bool:
        if self.process is None:
            return False

        cur_attempt = 0
        model_loading_time = 0
        model_loading_log_time = 1
        while True:
            try:
                response = requests.get(self.health_check_url)

                if response.status_code == 503:
                    if model_loading_time > max_wait_time_for_model_loading:
                        print(
                            f"Model failed to load in {max_wait_time_for_model_loading}. "
                            f"Consider increasing the waiting time for model loading."
                        )
                        return False

                    print(
                        f"model is still being loaded, or at full capacity. "
                        f"Will wait for {max_wait_time_for_model_loading - model_loading_time} "
                        f"more seconds: {response=}"
                    )
                    time.sleep(model_loading_log_time)
                    model_loading_time += model_loading_log_time
                    continue
                if response.status_code == 200:
                    print(f"Server started successfully, {response=}")
                    return True
                print(
                    f"Server is not responding properly, maybe model failed to load: {response=}"
                )
                return False

            except requests.exceptions.ConnectionError:
                print(
                    f"Couldn't establish connection, retrying with attempt: {cur_attempt}/{max_connection_attempts}"
                )
                cur_attempt += 1
                if cur_attempt > max_connection_attempts:
                    print(
                        f"Couldn't establish connection after {max_connection_attempts=}"
                    )
                    return False
            time.sleep(sleep_time_between_attempts)

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None

    def __del__(self):
        self.stop()
        del self
    
if __name__ == "__main__":    
    llama_server = LlamaServer(use_gpu=False)
    llama_server.start()
    