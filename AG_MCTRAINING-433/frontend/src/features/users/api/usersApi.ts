import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export interface User {
  userId: string
  name: string
  email: string
  status?: string
  createdAt?: string
}

export interface CreateUserPayload {
  name: string
  email: string
  userId?: string
}

export interface UpdateUserPayload {
  name?: string
  email?: string
}

export const usersApi = createApi({
  reducerPath: 'usersApi',
  baseQuery: fetchBaseQuery({
    baseUrl: import.meta.env.VITE_API_BASE_URL ?? '',
  }),
  // Keep cache alive for 5 minutes after all subscribers unmount (e.g. navigating away)
  keepUnusedDataFor: 300,
  refetchOnFocus: true,
  refetchOnReconnect: true,
  tagTypes: ['Users'],
  endpoints: (builder) => ({
    getUsers: builder.query<User[], void>({
      query: () => '/users',
      providesTags: ['Users'],
    }),
    getUser: builder.query<User, string>({
      query: (userId) => `/users/${userId}`,
      providesTags: (_result, _err, id) => [{ type: 'Users', id }],
    }),
    createUser: builder.mutation<{ message: string; userId: string }, CreateUserPayload>({
      query: (body) => ({ url: '/users', method: 'POST', body }),
      invalidatesTags: ['Users'],
    }),
    updateUser: builder.mutation<{ message: string }, { userId: string; body: UpdateUserPayload }>({
      query: ({ userId, body }) => ({ url: `/users/${userId}`, method: 'PUT', body }),
    }),
    deleteUser: builder.mutation<{ message: string }, string>({
      query: (userId) => ({ url: `/users/${userId}`, method: 'DELETE' }),
      invalidatesTags: ['Users'],
    }),
  }),
})

export const {
  useGetUsersQuery,
  useGetUserQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,
} = usersApi
