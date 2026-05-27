# 构建阶段
FROM node:22-alpine AS build-stage

RUN npm config set registry https://registry.npmmirror.com

WORKDIR /app
COPY package*.json ./
RUN npm ci && chmod -R 755 node_modules

# 复制其余文件（node_modules 已被 .dockerignore 排除，不会被覆盖）
COPY . .
# 再次确保权限万无一失
RUN chmod -R 755 node_modules
RUN npm run build

# 生产阶段
FROM nginx:stable-alpine
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]