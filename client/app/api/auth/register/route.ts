import { NextResponse } from "next/server"

export async function POST(request: Request) {
  const body = await request.json()
  // Pretend we created the user
  return NextResponse.json(
    {
      message: "Registered successfully",
      // echo back what we “created”
      user: {
        id: "user_mock",
        name: body.name || "New User",
        email: body.email,
        roles: ["sales"],
      },
    },
    { status: 201 },
  )
}
