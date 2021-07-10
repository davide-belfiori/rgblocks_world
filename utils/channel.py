import queue

class Channel:
    def __init__(self) -> None:
        self.out_queue = queue.Queue()
        self.in_queue = queue.Queue()
        self.server = Endpoint(self.in_queue, self.out_queue)

    def registerClient(self):
        return Endpoint(self.out_queue, self.in_queue)

class Endpoint:
    def __init__(self, input_queue, output_queue) -> None:
        self.input_queue = input_queue
        self.output_queue = output_queue

    def send(self, obj):
        self.output_queue.put(obj)

    def receive(self, block=True):
        if self.input_queue.empty():
            return None
        try:
            message = self.input_queue.get(block=block)
            if message != None:
                self.input_queue.task_done()
            return message
        except:
            return None

    def inputSize(self):
        return self.input_queue.qsize()

    def outputSize(self):
        return self.output_queue.qsize()
