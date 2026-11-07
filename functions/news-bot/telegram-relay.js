// Ретранслятор Telegram для бота новостей (Cloudflare Workers).
// 1) Бот → Telegram: пропускает запросы к api.telegram.org только с правильным ключом.
// 2) Telegram → бот: принимает вебхук на /hook и передаёт его функции в Yandex Cloud.
const KEY = "Dt7CVnFXrrrqp9K9OlBJMDkmdTsIFn3A";
const FUNCTION_URL = "https://functions.yandexcloud.net/d4ejsjlrsosgmi8b6nlk";

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname === "/hook") {
      if (request.method !== "POST" || request.headers.get("x-telegram-bot-api-secret-token") !== KEY) {
        return new Response("forbidden", { status: 403 });
      }
      const body = await request.text();
      const r = await fetch(FUNCTION_URL, {
        method: "POST",
        headers: { "content-type": "application/json", "x-telegram-bot-api-secret-token": KEY },
        body,
      });
      // функция отвечает готовым методом (например sendMessage) — Telegram выполнит его сам
      const answer = await r.text();
      return new Response(r.ok && answer.includes('"method"') ? answer : "ok",
        { headers: { "content-type": "application/json" } });
    }
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
