.PHONY: help build up down logs restart clean

help: ## 显示帮助信息
	@echo "可用的命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## 构建 Docker 镜像
	docker-compose build

up: ## 启动服务（开发模式）
	docker-compose up -d

up-prod: ## 启动服务（生产模式）
	docker-compose -f docker-compose.prod.yml up -d

down: ## 停止服务
	docker-compose down

logs: ## 查看日志
	docker-compose logs -f

logs-backend: ## 查看后端日志
	docker-compose logs -f backend

logs-frontend: ## 查看前端日志
	docker-compose logs -f frontend

restart: ## 重启服务
	docker-compose restart

clean: ## 清理容器和镜像
	docker-compose down -v
	docker system prune -f

rebuild: ## 重建镜像并启动
	docker-compose build --no-cache
	docker-compose up -d

status: ## 查看服务状态
	docker-compose ps
