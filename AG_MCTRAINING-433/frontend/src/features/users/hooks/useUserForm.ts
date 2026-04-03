import { useState, type ChangeEvent, type FormEvent } from 'react'
import { useDispatch } from 'react-redux'
import type { User } from '../api/usersApi'
import { usersApi, useCreateUserMutation, useUpdateUserMutation } from '../api/usersApi'
import { payrollApi } from '../../payroll/api/payrollApi'

interface FormValues {
  name: string
  email: string
}

interface FormErrors {
  name?: string
  email?: string
}

function validate(values: FormValues): FormErrors {
  const errors: FormErrors = {}
  if (!values.name.trim()) errors.name = 'Name is required.'
  if (!values.email.trim()) {
    errors.email = 'Email is required.'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
    errors.email = 'Enter a valid email address.'
  }
  return errors
}

export function useUserForm(initialValues: User | undefined, onSuccess: () => void) {
  const dispatch = useDispatch()
  const [values, setValues] = useState<FormValues>({
    name: initialValues?.name ?? '',
    email: initialValues?.email ?? '',
  })
  const [errors, setErrors] = useState<FormErrors>({})
  const [createUser, { isLoading: creating }] = useCreateUserMutation()
  const [updateUser, { isLoading: updating }] = useUpdateUserMutation()

  function handleChange(e: ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target
    setValues((prev) => ({ ...prev, [name]: value }))
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }))
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const errs = validate(values)
    if (Object.keys(errs).length > 0) {
      setErrors(errs)
      return
    }
    if (initialValues) {
      await updateUser({ userId: initialValues.userId, body: values })
      // No immediate invalidation (would fetch stale data). Delay to give Lambda time.
      // LocalStack cold starts can take 5-10s, so we fire at 5s and 10s.
      setTimeout(() => dispatch(usersApi.util.invalidateTags(['Users'])), 5000)
      setTimeout(() => dispatch(usersApi.util.invalidateTags(['Users'])), 10000)
    } else {
      await createUser(values)
      // The Lambda creates a payroll record asynchronously via SNS after user creation.
      // Delay the cache invalidation to give the Lambda time to finish, then
      // invalidate twice (at 3s and 6s) to handle slower LocalStack environments.
      setTimeout(() => dispatch(payrollApi.util.invalidateTags(['Payroll'])), 3000)
      setTimeout(() => dispatch(payrollApi.util.invalidateTags(['Payroll'])), 6000)
    }
    onSuccess()
  }

  function reset(next: User | undefined) {
    setValues({ name: next?.name ?? '', email: next?.email ?? '' })
    setErrors({})
  }

  return {
    values,
    errors,
    isSubmitting: creating || updating,
    handleChange,
    handleSubmit,
    reset,
  }
}

export { useUserForm as useForm }
