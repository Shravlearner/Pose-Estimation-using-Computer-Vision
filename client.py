import socket
import cv2
import pickle
import struct
import numpy as np
import os
import time
import queue
import threading

PORT = 5050
FORMAT = 'ISO-8859-1'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.0.160"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

recvData = b''
payload_size = struct.calcsize("L")

# Found on StackOverflow
# Function to calculate Structural Similarity Index for comparing images
def ssim(i1, i2):
    c1 = 6.5025
    c2 = 58.5225
    # INITS
    I1 = np.float32(i1) # cannot calculate on one byte large values
    I2 = np.float32(i2)
    I2_2 = I2 * I2 # I2^2
    I1_2 = I1 * I1 # I1^2
    I1_I2 = I1 * I2 # I1 * I2
    # END INITS
    # PRELIMINARY COMPUTING
    mu1 = cv2.GaussianBlur(I1, (11, 11), 1.5)
    mu2 = cv2.GaussianBlur(I2, (11, 11), 1.5)
    mu1_2 = mu1 * mu1
    mu2_2 = mu2 * mu2
    mu1_mu2 = mu1 * mu2
    sigma1_2 = cv2.GaussianBlur(I1_2, (11, 11), 1.5)
    sigma1_2 -= mu1_2
    sigma2_2 = cv2.GaussianBlur(I2_2, (11, 11), 1.5)
    sigma2_2 -= mu2_2
    sigma12 = cv2.GaussianBlur(I1_I2, (11, 11), 1.5)
    sigma12 -= mu1_mu2
    t1 = 2 * mu1_mu2 + c1
    t2 = 2 * sigma12 + c2
    t3 = t1 * t2                    # t3 = ((2*mu1_mu2 + C1).*(2*sigma12 + C2))
    t1 = mu1_2 + mu2_2 + c1
    t2 = sigma1_2 + sigma2_2 + c2
    t1 = t1 * t2                    # t1 =((mu1_2 + mu2_2 + C1).*(sigma1_2 + sigma2_2 + C2))
    ssim_map = cv2.divide(t3, t1)    # ssim_map =  t3./t1;
    mssim = cv2.mean(ssim_map)       # mssim = average of ssim map
    return mssim

count = 0
imagesCount = 0
previousFrame = -1
frameToDisplay = -1

# bufferless VideoCapture
class VideoCapture:

  def __init__(self, name):
    self.cap = cv2.VideoCapture(name)
    self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    self.q = queue.Queue()
    self.isOpened = True
    t = threading.Thread(target=self._reader)
    t.daemon = True
    t.start()

  # read frames as soon as they are available, keeping only most recent one
  def _reader(self):
    while True:
      ret, frame = self.cap.read()
      if not ret:
        break
      if not self.q.empty():
        try:
          self.q.get_nowait()   # discard previous (unprocessed) frame
        except queue.Empty:
          pass
      self.q.put(frame)
      time.sleep(0.016)
    self.isOpened = False

  def read(self):
    return self.q.get()

  def getIsOpened(self):
      return self.isOpened

startTime = time.time()

for x in os.listdir("videos"):
    # x = "Kettlebell Training - 12697.mp4"
    image_path = "videos/" + x
    video = VideoCapture(image_path)
    offClientTimes = []
    while video.getIsOpened() and count < 100:
        frame = video.read()
        frame = cv2.resize(frame, (640, 480))
        if count == 0:
            previousFrame = frame
            frameToDisplay = frame
        elif frame is not None:
            # Calculate difference between frames and whether it's unique enough to process
            frame_diff = ssim(previousFrame, frame)
            print("\frame_diff: R {}% G {}% B {}%".format(round(frame_diff[2] * 100, 2), round(frame_diff[1] * 100, 2),
                                                    round(frame_diff[0] * 100, 2)))

            if (frame_diff[2] * 100 * .33 + frame_diff[1] * 100 * .33 + frame_diff[0] * 100 * .33) < 98:
                # Send encoded frame data from client to server
                data = pickle.dumps(frame, 5)
                message_size = struct.pack("L", len(data))
                client.sendall(message_size + data)
                offClientStart = time.time()

                # Wait for server to run inference and send processed frame back
                while len(recvData) < payload_size:
                    recvData += client.recv(4096)
                packed_msg_size = recvData[:payload_size]
                recvData = recvData[payload_size:]
                msg_size = struct.unpack("L", packed_msg_size)[0]
                while len(recvData) < msg_size:
                    recvData += client.recv(4096)
                offClientTimes.append((time.time() - offClientStart) * 1000)

                # Convert processed frame from byte data to frame
                frame_data = recvData[:msg_size]
                recvData = recvData[msg_size:]
                frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")

                # frame_bytes = cv2.imencode('.jpg', frame)[1]
                # frame_bytes = np.array(frame_bytes, dtype = np.uint8).tobytes()

                # numberOfBytes = len(frame_bytes)
                # header = '' + str(numberOfBytes) + "\0"
                # rawHeader = bytes(header, FORMAT)
                # print("Sending {} bytes...".format(numberOfBytes))
                # print("Header is {}".format(header))
                # client.sendall(rawHeader)
                # client.sendall(frame_bytes)

                # rawReturn = []
                # recv_byte = client.recv(1)
                # while recv_byte != b"\0":
                #     rawReturn.append(recv_byte)
                #     recv_byte = client.recv(1)
                # print(rawReturn)
                # returnHeader = str(b''.join(rawReturn), FORMAT)
                # print("Expecting message of {} bytes".format(returnHeader))
                # returned_bytes = client.recv(262144)

                # # returnedText = client.recv(131072)
                
                # nparr = np.frombuffer(returned_bytes, dtype = np.uint8)
                # frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if frame is not None:
                    # print("Decoded successfully")
                    frameToDisplay = frame
                    previousFrame = frame
                    imagesCount += 1           

                # Display frame and updated previous frame
                cv2.imshow("Frame To Display", frameToDisplay)
                cv2.waitKey(1)
        count += 1
        time.sleep(0.25)

    count = 0
  
print("Total time elapsed (in ms): {}".format((time.time() - startTime) * 1000))
print("Images count is: {}".format(imagesCount))
print("Average inference time is: {}".format(sum(offClientTimes)/len(offClientTimes)))
