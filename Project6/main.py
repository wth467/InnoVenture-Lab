import argparse
from server.server import Server
from client.client import Client

def main():
    parser = argparse.ArgumentParser(description="Google Password Checkup Implementation")
    parser.add_argument("--server", action="store_true", help="Run in server mode")
    parser.add_argument("--client", action="store_true", help="Run in client mode")
    parser.add_argument("--password", type=str, help="Password to check (client mode)")
    parser.add_argument("--add", type=str, help="Password to add to database (server mode)")
    args = parser.parse_args()

    if args.server:
        server = Server()
        if args.add:
            server.add_password(args.add)
            print(f"Added password: {args.add}")
        else:
            print("Server running... (Use --add to add passwords)")
    
    elif args.client and args.password:
        client = Client()
        server = Server()  # 实际应用中应连接到远程服务器
        
        if client.check_password(args.password, server):
            print(f"WARNING: Password '{args.password}' is compromised!")
        else:
            print(f"Password '{args.password}' is safe.")
    else:
        print("Invalid arguments. Use --help for usage.")

if __name__ == "__main__":
    main()