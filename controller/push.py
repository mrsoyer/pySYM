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
        os.system('gcloud functions deploy sym --trigger-http --runtime python311 --allow-unauthenticated --region=europe-west1 --entry-point=http --set-env-vars '+env)