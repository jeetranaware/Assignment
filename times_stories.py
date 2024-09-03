import http.server
import socketserver
import urllib.request

PORT = 8000

class TimeStoriesHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/getTimeStories':
            stories_html = self.get_latest_stories()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(stories_html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_latest_stories(self):
        url = "https://time.com"
        response = urllib.request.urlopen(url)
        html = response.read().decode("utf-8")

        stories = []
        start_index = html.find('<div class="latest-stories">')
        if start_index != -1:
            html = html[start_index:]
            for _ in range(6):
                link_start = html.find('<a href="')
                if link_start == -1:
                    break
                link_end = html.find('"', link_start + 9)
                link = "https://time.com" + html[link_start + 9:link_end]

                title_start = html.find('>', link_end) + 1
                title_end = html.find('</a>', title_start)
                title = html[title_start:title_end].strip()

                title = title.split('>')[-1]

                stories.append(f'<li><a href="{link}" target="_blank">{title}</a></li>')

                html = html[title_end:]

        if not stories:
            stories_html = "<p>No stories found. The structure of Time.com may have changed.</p>"
        else:
            stories_html = f"""
            <html>
            <head>
                <title>Latest Time.com Stories</title>
            </head>
            <body>
                <h1>Latest 6 Stories from Time.com</h1>
                <ul>
                    {''.join(stories)}
                </ul>
            </body>
            </html>
            """
        
        return stories_html

with socketserver.TCPServer(("", PORT), TimeStoriesHandler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
