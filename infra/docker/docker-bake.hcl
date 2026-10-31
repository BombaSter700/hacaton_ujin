variable "DOCKER_REGISTRY" {
  default = "ghcr.io/programmisto"
}

variable "IMAGE_TAG" {
  default = "latest"
}

variable "TARGET_PLATFORM" {
  default = "linux/amd64"
}

group "default" {
  targets = ["programmisto_auth", "programmisto_emulators"]
}

target "programmisto_auth" {
  context    = "./backend"
  dockerfile = "auth/Dockerfile"
  tags       = ["${DOCKER_REGISTRY}/programmisto_auth:${IMAGE_TAG}"]
  platforms  = [TARGET_PLATFORM]
}

target "programmisto_emulators" {
  context    = "./backend/emulators"
  dockerfile = "Dockerfile"
  tags       = ["${DOCKER_REGISTRY}/programmisto_emulators:${IMAGE_TAG}"]
  platforms  = [TARGET_PLATFORM]
}
