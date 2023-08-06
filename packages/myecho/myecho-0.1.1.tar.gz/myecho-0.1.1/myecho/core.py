# Insert your code here. 
import argparse

def myecho():
    while True:
        line = input().strip()
        print(line)

def myecho_cmd():
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', '-t', type=str, help='一条消息', required=True)
    args = parser.parse_args()
    line = args.text
    print(line)
