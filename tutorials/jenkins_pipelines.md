# Jenkins pipelines

Jenkins Pipelines are used to define, manage, and automate the entire lifecycle of software delivery processes (a.k.a. CI/CD pipelines). 
These pipelines provide a structured way to define the steps and stages involved in **building**, **testing**, **deploying**, and **delivering** software applications. 

Jenkins Pipelines enable teams to automate repetitive tasks, and ensure consistent and reliable software releases.

### Motivation

Let's take the Docker images build process as an example...

In our development workflow, whenever we wanted to create a new version of our application, we had to manually run the `docker build` command to create a Docker image.
This process involved remembering the right set of build arguments, manually managing images, and we had no any mechanism to track the build history. 

With Jenkins Pipelines, we can automate the build process, which makes it consistent and reproducible process. 
In addition, Jenkins provides a clear view of the build status, logs, and any errors encountered during the build. 

## Create your first pipeline

### The `Jenkinsfile`

A Jenkins pipeline is defined in a file usually called `Jenkinsfile`, stored as part of the code repository.
In this file you instruct Jenkins on how to build, test, and deploy your application by specifying a series of stages, steps, and configurations.  

There are two main types of syntax for defining Jenkins pipelines in a Jenkinsfile: [Declarative Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/#declarative-pipeline) and [Scripted Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/#scripted-pipeline).

- Declarative syntax is a more structured and easy. It uses a predefined set of functions (a.k.a [directives](https://www.jenkins.io/doc/book/pipeline/syntax/#declarative-directives)) to define the pipeline's structure.
- Scripted syntax provides a more flexible and powerful way to define pipelines. It allows you to use Groovy scripting to customize and control every aspect of the pipeline. This pipelines won't be covered in this course.

The `Jenkinsfile` typically consists of multiple **stages**, each of which performs a specific **steps**, such as building the code as a Docker image, running tests, or deploying the software to Kubernetes cluster.

Let's create a declarative pipeline that builds aa docker image for the Roberta app.  

1. In your repository, in branch `main`, create a file called `build.Jenkinsfile` in the root directory as the following template:

```text
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'ls'
                sh 'echo building...'
            }
        }
    }
}
```

The Jenkinsfile you've provided is written in Declarative Pipeline syntax. Let's break down each part of the code:

- `pipeline { ... }`: This is the outermost block that encapsulates the entire pipeline definition.
- `agent any`: This directive specifies the [agent](https://www.jenkins.io/doc/book/using/using-agents/) where the pipeline stages will run. The `any` keyword indicates that the pipeline can run on any available agent (Jenkins agent or worker). Agents are the compute resources where the pipeline stages are executed.
- `stages { ... }`: The [stages block](https://www.jenkins.io/doc/book/pipeline/syntax/#stages) contains a series of stages that define the major steps in the pipeline. Stages represent different phases of the software delivery process.
- `stage('Build') { ... }`: This directive defines a specific stage named "Build." Each stage represents a logical phase of your pipeline, such as building, testing, deploying, etc.
- `steps { ... }:` Inside the stage block, the [steps block](https://www.jenkins.io/doc/book/pipeline/syntax/#steps) contains the individual steps or tasks to be executed within that stage.
- `sh 'echo building...'`: This directive is a step that executes a shell command. In this case, it uses the sh (shell) step to run the shell command 'echo building...'. This step prints "building..." to the console.

2. Commit and push your changes.

### Configure the pipeline in Jenkins

3. From the main Jenkins dashboard page, choose **New Item**.
4. Enter the project name (e.g. `RobertaBuild`), and choose **Pipeline**.
5. Check **GitHub project** and enter the URL of your GitHub repo.
6. Under **Build Triggers** check **GitHub hook trigger for GITScm polling**.
7. Under **Pipeline** choose **Pipeline script from SCM**.
8. Choose **Git** as your SCM, and enter the repo URL.
9. If you don't have yet credentials to GitHub, choose **Add** and create **Jenkins** credentials.
   1. **Kind** must be **Username and password**
   2. Choose informative **Username** (as **github** or something similar)
   3. The **Password** should be a GitHub Personal Access Token with the following scope:
      ```text
      repo,read:user,user:email,write:repo_hook
      ```
      Click [here](https://github.com/settings/tokens/new?scopes=repo,read:user,user:email,write:repo_hook) to create a token with this scope.
   4. Enter `github` as the credentials **ID**.
   5. Click **Add**.
10. Under **Branches to build** enter `main` as we want this pipeline to be triggered upon changes in branch main.
11. Under **Script Path** write the path to your `build.Jenkinsfile` defining this pipeline.
12. **Save** the pipeline.
13. Test the integration by add a [`sh` step](https://www.jenkins.io/doc/pipeline/tour/running-multiple-steps/#linux-bsd-and-mac-os) to the `build.Jenkinsfile`, commit & push and see the triggered job.

Well done! You've implemented an automated build pipeline for the Roberta app.

## Pipeline Execution

Let's discuss the execution stages when your pipeline is running:

1. **Job scheduling**: When you trigger a pipeline job, Jenkins schedules the job on one of its available **agents** (also known as nodes). Agents are the machines that actually execute the build steps. In our case, the pipline runs on the Jenkins server machine itself, known as the **built-in node**. This is very bad practice, and we will change it soon. Each agent can have one or more **executors**, which are worker threads responsible for running jobs concurrently.
2. **Workspace creation**: Jenkins creates a **workspace directory** on the agent's file system. This directory serves as the working area for the pipeline job.
3. **Checkout source code**: Jenkins checks out the source code into the workspace. 
4. **Pipeline execution**: Jenkins executes your pipeline script step-by-step. 

## The Build phase

The Build phase builds the app source code and store the **build artifact** somewhere, make it ready to be deployed.
In our case, a docker image is our build artifact, but in general, there are many other build tools that can be used in different programming languages and contexts (e.g. [maven](https://www.jenkins.io/doc/tutorials/build-a-java-app-with-maven/#fork-and-clone-the-sample-repository-on-github), `npm`, `gradle`, etc...)


#### Guidelines 

We now want to complete the `build.Jenkinsfile` pipeline, such that on every run of this job,
a new docker image of the app will be built and stored in container registry (DockerHub or ECR).

- Modify the `build.Jenkinsfile` to build an docker image and push it. Your stage might look like:

```text
stage('Build') {
   steps {
       sh '''
            docker login ...
            docker build ...
            docker tag ...
            docker push ...
       '''
   }
}
```

- Feel free to create other `stage`s according to your needs.  
- Your image should be pushed either to DockerHub or [ECR](https://console.aws.amazon.com/ecr/repositories) repo.
- You can use the timestamp, or the `BUILD_NUMBER` or `BUILD_TAG` [environment variables](https://www.jenkins.io/doc/book/pipeline/jenkinsfile/#using-environment-variables) to tag your Docker images, but don't tag the images as `latest`.
- If using ECR, give your EC2 instance an appropriate role to push an image to ECR.
- Use the [`environment` directive](https://www.jenkins.io/doc/book/pipeline/syntax/#environment) to store global variable and make your pipeline a bit more elegant. 

## The Deploy phase

Let's create another new Jenkins pipeline that **deploys** the image we've just built to a Kubernetes cluster.

We would like to **trigger** the Deploy pipeline after every successful running of the Build pipeline.

1. In the app repo, create another `Jenkinsfile` called `deploy.Jenkinsfile`. In this pipeline we will define the deployment steps for the roberta app:
```text
pipeline {
    agent any
    
    stages {
        stage('Deploy') {
            steps {
                // complete this code to deploy to real k8s cluster
                sh '# kubectl apply -f ....'
            }
        }
    }
}
``` 

2. In the Jenkins dashboard, create another Jenkins **Pipeline** (can be named `RobertaDeploy`), fill it similarly to the Build pipeline, but **don't trigger** this pipeline as a result of a GitHub hook event (why?).

We now want that every **successful** Build pipeline running will **automatically** trigger the Deploy pipeline. We can achieve this using the following two steps: 

3. In `build.Jenkinsfile`, add the [Pipeline: Build](https://www.jenkins.io/doc/pipeline/steps/pipeline-build-step/) function that triggers the Deploy pipeline:

```text
stage('Trigger Deploy') {
    steps {
        build job: '<deploy-job-name>', wait: false, parameters: [
            string(name: 'ROBERTA_IMAGE_URL', value: "<full-url-to-docker-image>")
        ]
    }
}
```

Where:
- `<deploy-job-name>` is the name of your Deploy pipeline (should be `RobertaDeploy`).
- `<full-url-to-docker-image>` is a full URL to the Docker image you've just built. You environment variable to make it dynamically according to the image tag. E.g. : `value: "${IMAGE_NAME}:${IMAGE_TAG}"`.

4. In the `deploy.Jenkinsfile` define a [string parameter](https://www.jenkins.io/doc/book/pipeline/syntax/#parameters) that will be passed to this pipeline from the Build pipeline:

```text
pipeline {
    agent ..
    
    # add the below line in the same level an `agent` and `stages`:
    parameters { string(name: 'ROBERTA_IMAGE_URL', defaultValue: '', description: '') }

    stages ...
}
```

Test your simple CI/CD pipeline end-to-end.

## The Build and Deploy phases - overview

![](../.img/build-deploy.png)

# Self-check questions

[Enter the interactive self-check page](https://alonitac.github.io/UPES-CSDV3001/multichoice-questions/jenkins_pipelines.html)

# Exercises 

## :pencil2: Clean the build artifacts from Jenkins server

Use the [`post` directive](https://www.jenkins.io/doc/book/pipeline/syntax/#post) and the [`docker image prune` command](https://docs.docker.com/config/pruning/#prune-images) to cleanup the built Docker images from the disk. 

## :pencil2: Fine tune the your pipelines

Review some additional pipeline features, as part of the [`options` directive](https://www.jenkins.io/doc/book/pipeline/syntax/#options). Add the `options{}` clause with the relevant features for the Build and Deploy pipelines.

## :pencil2: Clean the workspace after every build 

Jenkins does not clean the workspace by default after a build. 
Jenkins retains the contents of the workspace between builds to improve performance by avoiding the need to re-fetch and recreate the entire workspace each time a build runs.

Cleaning the workspace can help ensure that no artifacts from previous builds interfere with the current build.

Configure `stage('Clean Workspace')` stage to [clean the workspace](https://www.jenkins.io/doc/pipeline/steps/ws-cleanup/) before or after a build. 

## :pencil2: Security vulnerability scanning

Integrate `snyk` image vulnerability scanning into your build-deploy pipline.

#### Guidelines

- Create a **Secret text** Jenkins credentials containing the snyk API token.
- Use the [`withCredentials` step](https://www.jenkins.io/doc/pipeline/steps/credentials-binding/), read your Snyk API secret as `SNYK_TOKEN` env var, and perform the security testing using simple `sh` step and `synk` cli.
- Sometimes, Snyk alerts you for a vulnerability that has no update available, or that you do not believe to be currently exploitable in your application. You can ignore a specific vulnerability in a project using the [`snyk ignore`](https://docs.snyk.io/snyk-cli/test-for-vulnerabilities/ignore-vulnerabilities-using-snyk-cli) command:

```text
snyk ignore --id=<ISSUE_ID>
```

- **Bonus:** use [Snyk Jenkins plugin](https://docs.snyk.io/integrations/ci-cd-integrations/jenkins-integration-overview) or use the [Jenkins HTML publisher](https://plugins.jenkins.io/htmlpublisher/) plugin together with [snyk-to-html](https://github.com/snyk/snyk-to-html) project to generate a UI friendly Snyk reports in your pipeline page.

## :pencil2: Backup pipeline

Create a new Jenkins pipeline and code the corresponding `Jenkinsfile`, to periodically backup the Jenkins server in S3.

- In the Jenkinsfile, use bash script that compresses the `/var/lib/jenkins` directory into a `.tar.gz` file, [excluding some files](https://www.jenkins.io/doc/book/system-administration/backing-up/#back-up-the-controller-key-separately).
- Push the `.tar.gz` file to an S3 bucket.
- The pipeline should be running periodically once a day. 

## :pencil2: Shared libraries

https://www.jenkins.io/blog/2017/02/15/declarative-notifications/