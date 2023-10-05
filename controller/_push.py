import os



def run(request):
    current_script_path = os.path.abspath(__file__)
    current_script_directory = os.path.dirname(current_script_path)
    env_path = os.path.join(current_script_directory,'..', '.env')
    env = ""
    with open(env_path) as f:
        lines = f.readlines()
        #print(lines)
        for line in lines:
            #print(line)
            env = env+str(line).replace("\n",",")
        env = env[:-1]
        #print('gcloud functions deploy sym --trigger-http --runtime python311 --allow-unauthenticated --region=europe-west1 --entry-point=http --set-env-vars '+env+' --source  https://source.developers.google.com/projects/xtra-mobile-app/repos/github_mrsoyer_pysym/moveable-aliases/main/paths/.')
        os.system('git add .')
        os.system('git commit -m m')
        os.system('git push origin main')
        os.system('gcloud functions deploy sym --service-account sym-295@xtra-mobile-app.iam.gserviceaccount.com --trigger-http --runtime python311 --allow-unauthenticated --region=europe-west1 --entry-point=http --set-env-vars '+env+' --source https://source.developers.google.com/projects/xtra-mobile-app/repos/github_mrsoyer_pysym/revisions/main')
        