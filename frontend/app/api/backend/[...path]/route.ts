import { NextRequest, NextResponse } from "next/server";

const RAW_API_BASE =
  process.env.ATLAS_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://atlas-api-ctqk.onrender.com";

const API_BASE = RAW_API_BASE.replace(/\/$/, "");

type RouteContext = {
  params: Promise<{ path: string[] }>;
};

async function proxy(req: NextRequest, context: RouteContext) {
  const { path } = await context.params;

  const target = new URL(`${API_BASE}/${path.join("/")}`);

  req.nextUrl.searchParams.forEach((value, key) => {
    target.searchParams.set(key, value);
  });

  const method = req.method;
  const hasBody = !["GET", "HEAD"].includes(method);

  const upstream = await fetch(target.toString(), {
    method,
    headers: {
      "Content-Type": req.headers.get("content-type") || "application/json",
    },
    body: hasBody ? await req.text() : undefined,
    cache: "no-store",
  });

  const body = await upstream.text();

  return new NextResponse(body, {
    status: upstream.status,
    headers: {
      "Content-Type": upstream.headers.get("content-type") || "application/json",
    },
  });
}

export async function GET(req: NextRequest, context: RouteContext) {
  return proxy(req, context);
}

export async function POST(req: NextRequest, context: RouteContext) {
  return proxy(req, context);
}

export async function PUT(req: NextRequest, context: RouteContext) {
  return proxy(req, context);
}

export async function PATCH(req: NextRequest, context: RouteContext) {
  return proxy(req, context);
}

export async function DELETE(req: NextRequest, context: RouteContext) {
  return proxy(req, context);
}
