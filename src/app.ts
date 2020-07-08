"use strict";
import Koa from "koa";
import KoaRouter from "koa-router";

const app = new Koa();
const router = new KoaRouter();



router.get("/", async (ctx: Koa.Context) => {
	ctx.body = "Hello world!";
});


router.get("/hello/:name", async (ctx: Koa.Context) => {
	let name: String = ctx.params.name;
	ctx.body = `Hello ${name}!`;
});





app.use(router.routes());
app.listen(3000, () => console.log("Server started..."));