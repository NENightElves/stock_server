cd frontend && npm install && npm run generate
cd .. && rm -r ./src/static
cp -r frontend/.output/public ./src/static
