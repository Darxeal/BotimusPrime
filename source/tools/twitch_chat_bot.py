import re
import socket

class TwitchChatBot:
    HOST = "irc.twitch.tv"
    PORT = 6667

    def __init__(self, username, oauth, channel):
        self.username = username
        self.oauth = oauth
        self.channel = channel

        self.con = socket.socket()
        self.con.connect((self.HOST, self.PORT))
        self.send_pass(oauth)
        self.send_nick(username)
        self.join_channel(channel)
        print(f"Joined channel {channel} as {username}")

        self.data = ""

    def send_pong(self, msg):
        self.con.send(bytes('PONG %s\r\n' % msg, 'UTF-8'))


    def send_message(self, message):
        self.con.send(bytes('PRIVMSG %s :%s\r\n' % (self.channel, message), 'UTF-8'))


    def send_nick(self, nick):
        self.con.send(bytes('NICK %s\r\n' % nick, 'UTF-8'))


    def send_pass(self, password):
        self.con.send(bytes('PASS %s\r\n' % password, 'UTF-8'))


    def join_channel(self, chan):
        self.con.send(bytes('JOIN %s\r\n' % chan, 'UTF-8'))


    def part_channel(self, chan):
        self.con.send(bytes('PART %s\r\n' % chan, 'UTF-8'))


    def get_sender(self, msg):
        result = ""
        for char in msg:
            if char == "!":
                break
            if char != ":":
                result += char
        return result


    def get_message(self, msg):
        result = ""
        i = 3
        length = len(msg)
        while i < length:
            result += msg[i] + " "
            i += 1
        result = result.lstrip(':')
        return result

    def scan(self):
        try:
            self.data += self.con.recv(1024).decode('UTF-8')
            data_split = re.split(r"[~\r\n]+", self.data)
            self.data = data_split.pop()

            for line in data_split:
                line = str.rstrip(line)
                line = str.split(line)

                if len(line) >= 1:
                    if line[0] == 'PING':
                        self.send_pong(line[1])

                    if line[1] == 'PRIVMSG':
                        sender = self.get_sender(line[0])
                        message = self.get_message(line).strip()

                        print(sender + ": " + message)

                        self.on_message(sender, message)

        except socket.error:
            print("Socket died")

        except socket.timeout:
            print("Socket timeout")

    def on_message(self, sender, message):
        """Override this method to handle received messages"""
        pass