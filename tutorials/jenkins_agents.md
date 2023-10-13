# Jenkins agents

We now want to focus on the machine in which Jenkins executes jobs. 
So far, all jobs have been executed in the Jenkins server itself. But this is far from being optimal. Why?

- Performance: Many heavy jobs can reduce the server performance. The Jenkins server should be free to schedule the jobs, but not to execution them.
- Build environments: What if we need to execute jobs on Windows environment, while the Jenkins server is running on Linux?
- Isolation: A job script can potentially access Jenkins secrets files, or data of another job, or to configure the OS in a way that impacting other currently running jobs. Remind yourself that Jenkins is a central platform that has access to all environments, it's deploying our apps to production as well as development environment. We want a complete isolation between jobs. 

Instead, let's introduce [distributed builds architecture](https://www.jenkins.io/doc/book/scaling/architecting-for-scale/#distributed-builds-architecture), while delegating the jobs execution to other machine(s), which will be called **Jenkins agents**.

Jenkins agents, also known as Jenkins slaves, are a fundamental part of the Jenkins automation system. They serve as the execution environment for Jenkins builds and tasks. 

![](../.img/jenkinsagent.png)

(Image by https://foxutech.com/author/motoskia/)


## Use Docker as Jenkins agent

The first step is to run jobs **within a docker containers**. The containers will still be running on the Jenkins server itself, later on we will integrate other agents and execute the containers on them. 

🧐 **Question**: Taking the factors mentioned above (performance, build environments and isolation), which of them have been achieved by running jobs in containers?

Let's create a Docker image that will be used as a **build agent** for our existed pipelines. One image for all pipelines. 
The image will be based on the [jenkins/agent](https://hub.docker.com/r/jenkins/agent/) image, 
which is suitable for running Jenkins jobs (with Java installed and other executable Jenkins uses).

What else do we need in this image to run our pipelines? We need `aws` cli, `docker`, `snyk`, `python`, and maybe more... very rich and colorful Docker image! 
We are going to utilize Docker [multistage builds](https://docs.docker.com/build/building/multi-stage/) for that. 

Take a look on the following Dockerfile:

```dockerfile
FROM ubuntu:latest as installer
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN apt-get update \
  && apt-get install -y unzip \
  && unzip awscliv2.zip \
  && ./aws/install --bin-dir /aws-cli-bin/

# this is an example demostrating how to install a tool on a some Docker image, then copy its artifacts to another image
RUN mkdir /snyk && cd /snyk \
    && curl https://static.snyk.io/cli/v1.666.0/snyk-linux -o snyk \
    && chmod +x ./snyk

FROM jenkins/agent

# Copy the `docker` (client only!!!) from `docekr` image to this image.
COPY --from=docker /usr/local/bin/docker /usr/local/bin/
COPY --from=installer /usr/local/aws-cli/ /usr/local/aws-cli/
COPY --from=installer /aws-cli-bin/ /usr/local/bin/
COPY --from=installer /snyk/ /usr/local/bin/
```

The dockerfile starts with [`ubuntu:latest`](https://hub.docker.com/_/ubuntu) as an `installer` image in which we will install `aws` cli and [`snyk`](https://docs.snyk.io/snyk-cli).
After the `installer` image was built, we will copy the relevant artifacts to the main image, the one starting with `FROM jenkins/agent`.

1. Build the image.
2. Push your image to a dedicated container registry in ECR or DockerHub.
3. In the `build.Jenkinsifle`, replace `agent any` by:

```text
agent {
    docker {
        image '<image-url>'       
        args  '--user root -v /var/run/docker.sock:/var/run/docker.sock'
    }
}
```

This directive tell Jenkins to run the pipeline on a docker container.

**Now pay attention!!!** Since as part of the build pipeline (`RobertaBuild`) we build a docker image, there is a [problem](https://jpetazzo.github.io/2015/09/03/do-not-use-docker-in-docker-for-ci/) of building a docker image from within a docker container, also known as [**dind** - docker in docker](https://hub.docker.com/_/docker). 
To solve this, we want the use the docker client **within** the agent container, to send the `docker build` command to the daemon resides **outside** the container, on the Jenkins server. This way we bypass the docker-in-docker problem, as the image is actually being built outside the container. Only the build command is sent from within the container. How do we do that? 

- The `-v` mount the socket file that the _docker client_ is using to talk with the _docker daemon_. In this case the docker client **within** the container will talk with the docker daemon operates **outside** the container on Jenkins machine.  
- The `--user root` runs the container as `root` user, which is necessary to access `/var/run/docker.sock`.

4. Test your pipeline on the Docker-based agent.

## Create and integrate new agents nodes

### Terminology

Source reference: https://www.jenkins.io/doc/book/managing/nodes/

#### Jenkins controller

The Jenkins controller is the Jenkins service itself and where Jenkins is installed. It is also a web server that also acts as a "brain" for deciding how, when, and where to run tasks. 

#### Nodes

Nodes are the "machines" on which build agents run. Jenkins monitors each attached node for disk space, free temp space, free swap, clock time/sync, and response time.
A node is taken offline if any of these values go outside the configured threshold. Jenkins supports two types of nodes:

- **Agents** - an agent is a small (170KB single `jar`) Java client process that connects to a Jenkins controller
- **Built-in node** (exists within the controller)

#### Executors

An executor is a slot for the execution of tasks. Effectively, it is a thread in the agent. The number of executors on a node defines the number of concurrent tasks that can run. 

## Create Jenkins agents

You can either choose to install a [Jenkins agent on Windows](https://www.jenkins.io/doc/book/managing/nodes/#installing-a-jenkins-agent-on-windows), [on MacOS](https://www.jenkins.io/doc/book/managing/nodes/#creating-a-macos-agent-for-jenkins), or deploy agent on EC2 instance (bellow). 

### Create an EC2 based agent 

Let's create an EC2 and connect it to your Jenkins controller as an agents.

1. Create an Ubuntu `*.micro` EC2 instance in the same VPC as your Jenkins server. Your instance has to have Java 11 and Docker installed. Make sure you have enough disk to execute your pipelines. It's recommended to create an AMI from this instance to later usage.
3. Go to **Manage Jenkins** > **Manage Nodes and Clouds** > **New Node**.
2. Give your node a name. E.g. `EC2 agent 1`.
3. Choose the option **Permanent Agent** and click **Ok**.
4. In **Number of executors** it's recommended to choose a value according to the number of CPUs of your agents machine. 
5. Under **Remote root directory** specify a directory on the agent where Jenkins will store files, it can be any directory that the `ubuntu` user has access to. E.g. `~/jenkins` or any other path.
4. Assign a label to the agent, e.g. `general`. The label will be later used to assign jobs specifically on an agent having this label.
5. In the **Launch method** section, select **Launch agents via SSH**.
6. Fill in the SSH details for your EC2 instance:
   - Host: Enter the private IP address of your EC2 instance.
   - Credentials: Choose or create the SSH credentials that allow Jenkins to connect to your EC2 instance.
   - Host Key Verification Strategy: Choose **Non verifying Verification Strategy**
   
   Click **Save** to save the configuration.
7. On the **Nodes** page, find your newly created agent and click on it, click on **Launch agent** from the left-hand menu.
8. Configure the `build.Jenkinsfile` pipeline to b executed on agents labeled according to the label you choose. For example:

```text
agent {
    docker {
        label 'general'
        image '<image-url>'       
        args  '--user root -v /var/run/docker.sock:/var/run/docker.sock'
    }
}
```

Trigger the pipeline and make sure it's running on the agents machine. 


## Exercises 

### :pencil2: Execute your pipelines in a container in a Jenkins agent

Complete the above work to configure the `build.Jenkinsfile`, `deploy.Jenkinsfile` and `pr-testing.Jenkinsfile` pipelines to be running on the Jenkins agent, in a Docker container.

Notes:

- As the `pr-testing.Jenkinsfile` require Python as part of the pipeline execution, you have to re-build the agent docker image with Python in it. You are highly encouraged to use another "installer" image to create Python virtual environment (`venv`) within the image, and then to copy the created `venv` to the `jenkins/agent` image.
- You have to [install kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) on the agent docker image.


### :pencil2: Autoscale the EC2 inatance agents nodes

Jenkins [EC2-plugin](https://plugins.jenkins.io/ec2/) allows Jenkins to start agents on EC2 on demand, and kill them as they get unused.
It'll start instances using the EC2 API and automatically connect them as Jenkins agents. When the load goes down, excess EC2 instances will be terminated.

1. Install the `Amazon EC2` Jenkins plugin. 
2. Once installed, navigate to the main **Manage Jenkins** > **Nodes and Clouds** page, and choose **Configure Clouds**.
3. Add an **Amazon EC2** cloud and configure it.
4. Test your configured "cloud" with some of your pipelines.

### :pencil2: Jenkins on k8s with agents as Pods

In this exercise, you will set up Jenkins on a Kubernetes cluster using Helm and configure Jenkins agents as pods to dynamically provision build environments.

1. [Install Jenkins](https://artifacthub.io/packages/helm/jenkinsci/jenkins) on your Kubernetes cluster using Helm.
2. Configure the [Kubernetes Plugin](https://plugins.jenkins.io/kubernetes/) in Jenkins to enable agent provisioning on the Kubernetes cluster.
3. Test the systems by running some pipeline. 