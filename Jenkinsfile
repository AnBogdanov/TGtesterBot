pipeline {
    agent {
        label 'master'
    }
    stages {
        stage("Build bot") {
            steps {
                cleanWs()
                checkout scm
                sh "docker stop telegram_bot"
                sh "docker rm telegram_bot"
                sh "docker rmi telegram_bot"
                sh "docker build -t telegram_bot ."
            }
        }
        stage("Run bot") {
            steps {
                sh "docker create --name telegram_bot telegram_bot"
                sh "sudo docker cp /root/dev/bot_test/conf.ini telegram_bot:/app/"
                sh "sudo docker cp /root/dev/ssh/Bot.uu telegram_bot:/app/"
                sh "docker start telegram_bot"
            }
        }

    }
}
