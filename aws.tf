variable "access_key" {}

variable "secret_key" {}

variable "private_key_file" {}

variable "public_key_file" {}

variable "region" {
  default = "us-east-2"
}

variable "vpc_id" {
  default = "vpc-f3a80d9b"
}

variable "keypair_name" {}

provider "aws" {
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
  region     = "${var.region}"
}

resource "aws_key_pair" "terraform_ec2_key" {
  key_name = "${var.keypair_name}"
  public_key = "${file("${var.public_key_file}")}"
}

resource "aws_subnet" "public_subnet_a" {
  vpc_id = "${var.vpc_id}"
  cidr_block = "172.31.64.0/20"
  tags = {
    "Name" = "dan_subnet"
  }
  map_public_ip_on_launch = true
  availability_zone = "${var.region}a"
}

resource "aws_security_group" "allow_web" {
  name        = "allow_web"
  description = "Allow 8888 inbound traffic"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8888
    to_port     = 8888
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    cidr_blocks     = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "dan_takehome" {
  ami           = "ami-5e8bb23b"
  instance_type = "m5.large"
  subnet_id = "${aws_subnet.public_subnet_a.id}"
  vpc_security_group_ids = ["${aws_security_group.allow_web.id}"] 
  key_name = "${var.keypair_name}"

  ebs_block_device {
    device_name = "/dev/sda1"
    volume_type = "gp2"
    volume_size = 30
  }

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update
              sudo mkdir /home/ubuntu/work
              sudo chown ubuntu:ubuntu /home/ubuntu/work
              sudo mv /tmp/takehome.ipynb /home/ubuntu/work/takehome.ipynb
              sudo mv /tmp/2010_Census_Population_By_Zipcode_ZCTA.csv /home/ubuntu/work/2010_Census_Population_By_Zipcode_ZCTA.csv
              sudo mv /tmp/New_York_City_Population_By_Neighborhood_Tabulation_Areas.csv /home/ubuntu/work/New_York_City_Population_By_Neighborhood_Tabulation_Areas.csv
              curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
              sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
              sudo apt-get update
              sudo apt-get install -y docker-ce
              sudo docker pull jupyter/datascience-notebook
              sudo docker run -d -v /home/ubuntu/work:/home/jovyan/work -p 8888:8888 jupyter/datascience-notebook start-notebook.sh --NotebookApp.token=''
              EOF

  provisioner "file" {
    source = "takehome.ipynb"
    destination = "/tmp/takehome.ipynb"
    connection {
      type = "ssh"
      user = "ubuntu"
      private_key = "${file("${var.private_key_file}")}"
    }
  }

  provisioner "file" {
    source = "2010_Census_Population_By_Zipcode_ZCTA.csv"
    destination = "/tmp/2010_Census_Population_By_Zipcode_ZCTA.csv"
    connection {
      type = "ssh"
      user = "ubuntu"
      private_key = "${file("${var.private_key_file}")}"
    }
  }

  provisioner "file" {
    source = "New_York_City_Population_By_Neighborhood_Tabulation_Areas.csv"
    destination = "/tmp/New_York_City_Population_By_Neighborhood_Tabulation_Areas.csv"
    connection {
      type = "ssh"
      user = "ubuntu"
      private_key = "${file("${var.private_key_file}")}"
    }
  }

}

