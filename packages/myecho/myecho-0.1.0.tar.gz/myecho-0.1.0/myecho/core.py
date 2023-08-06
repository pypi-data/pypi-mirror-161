# Insert your code here. 
import argparse

def echo():
    while True:
        line = input().strip()
        print(line)

def echo_cmd():
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', '-t', type=str, help='一条消息', required=True)
    args = parser.parse_args()
    line = args.text
    print(line)
