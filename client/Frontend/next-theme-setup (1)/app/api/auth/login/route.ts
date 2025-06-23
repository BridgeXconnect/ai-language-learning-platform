import { NextResponse } from "next/server"

export async function POST(request: Request) {
  // In a real system you'd validate the credentials.
  // Here, we just succeed for ANY input.
  const body = await request.json()
  const { email } = body

  return NextResponse.json(
    {
      access_token: "mock_access_token",
      refresh_token: "mock_refresh_token",
      user: {
        id: "user_mock",
        name: email.split("@")[0],
        email,
        roles: ["sales"], // default role for preview
      },
    },
    { status: 200 },
  )
}
