FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
# 复制构建产物
COPY --from=build /app/dist /usr/share/nginx/html
# 使用 nginx 官方镜像的 envsubst 模板机制：启动时把 ${BACKEND_URL}/${BACKEND_HOST} 注入
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
# 默认值（compose / NAS 场景）；Zeabur 上由环境变量覆盖为后端公网域名
ENV BACKEND_URL=http://backend:8000 \
    BACKEND_HOST=backend \
    NGINX_ENVSUBST_FILTER=BACKEND
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
