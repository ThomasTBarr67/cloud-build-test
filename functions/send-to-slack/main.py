def send_to_slack(event, context):
    import requests
    from google.cloud import secretmanager

    client = secretmanager.SecretManagerServiceClient()
    name = "projects/204024561480/secrets/slack_webhook/versions/latest"
    response = client.access_secret_version(request={"name": name})
    webhook_url = response.payload.data.decode("UTF-8")

    build_status = event.get('attributes').get('status')
    build_id = event.get('attributes').get('buildId')
    if build_status == 'SUCCESS':
        slack_text = f':large_green_circle: Cloud Build Success for {build_id}'
    elif build_status == 'FAILURE':
        slack_text = f':red_circle: ATTENTION! Cloud Build {build_id} did not succeed. Status is {build_status}.'
    slack_message = dict(text=slack_text)
    requests.post(webhook_url, json=slack_message)
