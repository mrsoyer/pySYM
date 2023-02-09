import os
def run(request,SYM):
    os.system('gcloud functions deploy pySYM_S --trigger-http --runtime python310 --allow-unauthenticated --region europe-west1 --entry-point=http')
    os.system('gcloud functions deploy pySYM_pubsub --trigger-topic="sym" --runtime python310 --allow-unauthenticated --region europe-west1 --entry-point=pubSub')