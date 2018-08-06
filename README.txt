Running the take home project:

The project uses the Jupyter Data Science Notebook docker image running on AWS and launched from terraform. To create the instance after cloning the repository:

1. From the command prompt in the git directory, initialize terraform:
> terraform init
2. Create a public/private key pair to use to communicate with the instance and give it a unique name:
> ssh-keygen -f YOUR_KEYNAME_HERE
3. Run the terraform deployment, passing valid access and secret keys at the prompts along with the location of the public and private keys you just created and the name you want AWS to use for the key pair:
> terraform apply

Once its complete, Jupyter should be running on the instance on port 8888. It might take a minute for the docker instance to be fully running. The instance should have a public IP viewable in the AWS management console with port 8888 already open.
