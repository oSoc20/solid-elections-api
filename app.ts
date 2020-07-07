"use strict";
import * as Koa from "koa";
import * as KoaRouter from "koa-router";

const app = new Koa();
const router = new KoaRouter();



router.get("/", async (ctx) => {
	ctx.body = "Hello world!";
});


router.get("/hello/:name", async (ctx) => {
	let name = ctx.params.name;
	ctx.body = `Hello ${name}!`;
});





app.use(router.routes());
app.listen(3000, () => console.log("Server started..."));