import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

export async function GET() {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!supabaseUrl || !supabaseAnonKey) {
    return NextResponse.json(
      {
        status: "error",
        db: "disconnected",
        message:
          "Missing NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY. Copy .env.example to .env.local and add your Supabase credentials.",
      },
      { status: 503 },
    );
  }

  try {
    const supabase = await createClient();
    const { count, error } = await supabase
      .from("health_checks")
      .select("*", { count: "exact", head: true });

    if (error) {
      return NextResponse.json(
        {
          status: "error",
          db: "disconnected",
          message: error.message,
        },
        { status: 503 },
      );
    }

    return NextResponse.json({
      status: "ok",
      db: "connected",
      healthCheckCount: count ?? 0,
    });
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Unknown database error";

    return NextResponse.json(
      {
        status: "error",
        db: "disconnected",
        message,
      },
      { status: 503 },
    );
  }
}
