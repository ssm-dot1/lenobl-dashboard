// Ретранслятор Telegram Bot API для бота новостей (Cloudflare Workers).
// Пропускает только запросы бота с правильным ключом и только к api.telegram.org.
const KEY = "Dt7CVnFXrrrqp9K9OlBJMDkmdTsIFn3A";

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (request.headers.get("x-relay-key") !== KEY) {
      return new Response("forbidden", { status: 403 });
    }
    if (!/^\/bot\d+:[\w-]+\/\w+$/.test(url.pathname)) {
      return new Response("bad request", { status: 400 });
    }
    const init = { method: request.method, headers: { "content-type": "application/json" } };
    if (request.method === "POST") init.body = await request.text();
    return fetch("https://api.telegram.org" + url.pathname, init);
  },
};
