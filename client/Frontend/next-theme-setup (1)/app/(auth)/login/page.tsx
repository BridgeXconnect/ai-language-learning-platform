import { LoginForm } from "@/components/auth/login-form"
import { Building } from "lucide-react"

export default function LoginPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-muted/40 p-4">
      <div className="flex items-center gap-2 font-semibold text-2xl mb-8 text-primary">
        <Building className="h-8 w-8" />
        <span>Dynamic Course Creator</span>
      </div>
      <LoginForm />
    </div>
  )
}
