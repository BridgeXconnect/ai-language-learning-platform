import { NextResponse } from "next/server"

export async function GET(request: Request) {
  // Very naive “auth” check – production code should verify JWTs
  const auth = request.headers.get("authorization") || ""
  if (!auth.includes("mock_access_token")) {
    return NextResponse.json({ message: "Unauthorized" }, { status: 401 })
  }

  return NextResponse.json(
    {
      id: "user_mock",
      name: "Preview User",
      email: "preview@example.com",
      roles: ["sales"],
    },
    { status: 200 },
  )
}
