import { create } from "zustand";
import { axiosInstance } from "../lib/axios";
import toast from "react-hot-toast";

export const useAuthStore = create((set) => ({
  authUser: null,
  isSigningUp: false,
  isLoggingIn: false,
  isCheckingAuth: true,

  // Check if user is already authenticated (called from a useEffect in App if needed)
  checkAuth: async () => {
    set({ isCheckingAuth: true });
    try {
      const res = await axiosInstance.get("http://localhost:8000/api/v1/auth/check-auth");
      set({ authUser: res.data });
    } catch (error) {
      console.log("Auth check failed:", error.response?.data?.detail);
      //toast.error(error?.response?.data?.detail[0]?.msg ||error.response?.data?.detail);
      set({ authUser: null });
    } finally {
      set({ isCheckingAuth: false });
    }
  },

  signup: async (data) => {
    set({ isSigningUp: true });
    try {
      const res = await axiosInstance.post("http://localhost:8000/api/v1/auth/signup", data);
      console.log(res.data);
      
      set({ authUser: res.data });
      toast.success("Account created successfully");
      return 1
    } catch (error) {
      console.log(error);
      const message = error?.response?.data?.detail[0]?.msg ||error?.response?.data?.detail ||  error.message || "Signup failed";
      toast.error(message);
      set({ authUser: null })
      return 0
      throw error; // Re-throw to let the form handle it
    } finally {
      set({ isSigningUp: false });
     
    }
  },

  login: async (data) => {
    set({ isLoggingIn: true });
    try {
      const res = await axiosInstance.post("http://localhost:8000/api/v1/auth/login", data);
      set({ authUser: res.data });
      toast.success("Logged in successfully");
      return 1
    } catch (error) {
      const message = error?.response?.data?.detail[0]?.msg || error?.response?.data?.detail || error?.response?.data?.message || error.message || "Login failed";
      toast.error(message);
      set({ authUser: null })
       return 0
      throw error; // Re-throw to let the form handle it
    } finally {
      set({ isLoggingIn: false });
   
    }
  },

  logout: async () => {
    try {
      await axiosInstance.post("http://localhost:8000/api/v1/auth/logout");
      set({ authUser: null });
      toast.success("Logged out successfully");
      window.location.href = "/login"; // <--- Redirect here
    } catch (error) {
      const message =error?.response?.data?.detail[0]?.msg ||error?.response?.data?.detail || error?.response?.data?.message || error.message || "Logout failed";
      toast.error(message);
    }
  },
}));
