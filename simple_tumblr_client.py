#!/usr/bin/env python3
import wolff_api_plugins.client.api_hook as hook
import wolff_api_plugins.client.client as client
import wolff_api_plugins.client.server_connection as conn
import wolff_api_plugins.client.oauth_credentials as cred

def main():
        auth = cred.OAuth1Credentials()
        auth.get_from_file( 'tumblr_keys.tsv' )

        print( auth.as_dict() )

        connect = conn.TCPServerConnection( ip = "127.0.0.1",
                                            port = 5555
        )

        args = { 'blog_id': '' }
        # '/v2/blog/loratest.tumblr.com/info',
        get_info = hook.APIMethod( uri = '/v2/blog/:blog_id/info',
                                         args = args,
                                         http_method = 'get',
                                         name = 'get_info'
        )

        args = { 'blog_id': '',
                 'type': '',
                 'body': '',
                 'title':''
               }

        post_blog = hook.APIMethod( uri = '/v2/blog/:blog_id/posts',
                                    args = args,
                                    http_method = 'post',
                                    name = 'post_blog'
        )

        args = { 'blog_id': '' }
        get_following = hook.APIMethod( uri = '/v2/blog/:blog_id/following',
                                        http_method = 'get',
                                        name = 'get_following',
                                        args = args
                                      )


        methods = [ get_info, post_blog, get_following ]

        tumblr_hook =  hook.APIHook( 'https://api.tumblr.com',
                                     methods = methods
        )



        # blog identifier uri example
        # https://api.tumblr.com/v2/blog/{blog-identifier}/

        tumblr_client = client.Client( connection = connect, endpoint = tumblr_hook,
                                       credentials = auth
        )

        tumblr_client.specialize()

        # resp = tumblr_client.get_nfo( blog_id = 'loratest.tumblr.com' )
        resp = tumblr_client.post_blog( blog_id = 'loratest.tumblr.com',
                                        type = "text",
                                        body =  "Hello world!",
                                        title = "the title"
                                      )

        # resp = tumblr_client.get_following( blog_id = 'loratest.tumblr.com' )
        print( resp )

if __name__ == '__main__':
    main()
