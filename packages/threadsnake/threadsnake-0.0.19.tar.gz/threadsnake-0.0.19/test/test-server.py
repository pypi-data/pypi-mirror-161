from threadsnake.core import *

set_log_config(LogLevel.ALL)
badge_async('threadsnake 0.0.15', title='version')

app = Application(get_port(8088))

#Configuring top level middlewares
app.configure(static_files('static'))
app.configure(session(Session('threadsnake-session-id')))
app.configure(authorization)
app.configure(body_parser)
app.configure(multipart_form_data_parser('temp', 60))
app.configure(json_body_parser)
app.configure(cors)
app.configure(default_headers(build_default_headers({"purpose":"test"})))
app.configure(identify_client)
app.configure(header_inspector("content-type", lambda a: print(a)))
app.configure(time_measure)
app.configure(uses_php('php', 'php', 8086))
app.configure(serve_static_markdown('markdown'))

#Configuring routers
app.use_router(routes_to('routers/users'), '/users')

@app.get('/test-api/base-endpoint')
def test_api_base_endpoint(app:Application, req:HttpRequest, res:HttpResponse):
    res.end('ready!')

app.wait_exit('')