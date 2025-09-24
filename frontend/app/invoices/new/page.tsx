/**
 * Licensed under the Business Source License 1.1 (BSL).
 * See LICENSE file for full terms.
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { format } from "date-fns";
import toast from "react-hot-toast";
import { Plus, Trash2 } from "lucide-react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

// Form validation schema
const invoiceItemSchema = z.object({
  name: z.string().min(1, "Nazwa jest wymagana"),
  quantity: z.number().min(0.01, "Ilość musi być większa niż 0"),
  unit: z.string().min(1, "Jednostka jest wymagana"),
  net_price: z.number().min(0.01, "Cena netto musi być większa niż 0"),
  vat_rate: z.number().min(0).max(23, "Stawka VAT musi być między 0 a 23"),
});

const invoiceSchema = z.object({
  company_id: z.string().uuid("Wybierz firmę"),
  invoice_number: z.string().min(1, "Numer faktury jest wymagany"),
  issue_date: z.string().min(1, "Data wystawienia jest wymagana"),
  sale_date: z.string().min(1, "Data sprzedaży jest wymagana"),
  due_date: z.string().min(1, "Termin płatności jest wymagany"),
  payment_method: z.string().min(1, "Wybierz metodę płatności"),
  contractor_data: z.object({
    nip: z.string().regex(/^\d{10}$/, "NIP musi mieć 10 cyfr"),
    name: z.string().min(1, "Nazwa kontrahenta jest wymagana"),
    address: z.object({
      street: z.string().min(1, "Ulica jest wymagana"),
      city: z.string().min(1, "Miasto jest wymagane"),
      postal_code: z.string().regex(/^\d{2}-\d{3}$/, "Kod pocztowy musi być w formacie XX-XXX"),
      country: z.string().default("PL"),
    }),
  }),
  items: z.array(invoiceItemSchema).min(1, "Dodaj przynajmniej jedną pozycję"),
});

type InvoiceFormData = z.infer<typeof invoiceSchema>;

export default function NewInvoicePage() {
  const router = useRouter();
  const [items, setItems] = useState([{
    name: "",
    quantity: 1,
    unit: "szt.",
    net_price: 0,
    vat_rate: 23,
  }]);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<InvoiceFormData>({
    resolver: zodResolver(invoiceSchema),
    defaultValues: {
      issue_date: format(new Date(), "yyyy-MM-dd"),
      sale_date: format(new Date(), "yyyy-MM-dd"),
      due_date: format(new Date(Date.now() + 14 * 24 * 60 * 60 * 1000), "yyyy-MM-dd"),
      payment_method: "transfer",
      contractor_data: {
        country: "PL",
      },
      items: items,
    },
  });

  // Fetch user's companies
  const { data: companies } = useQuery({
    queryKey: ["companies"],
    queryFn: () => api.get("/companies").then(res => res.data),
  });

  // Create invoice mutation
  const createInvoiceMutation = useMutation({
    mutationFn: (data: InvoiceFormData) => api.post("/invoices", data),
    onSuccess: (response) => {
      toast.success("Faktura została utworzona i przekazana do KSeF!");
      router.push(`/invoices/${response.data.id}`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Błąd podczas tworzenia faktury");
    },
  });

  const onSubmit = (data: InvoiceFormData) => {
    data.items = items.filter(item => item.name); // Remove empty items
    createInvoiceMutation.mutate(data);
  };

  const addItem = () => {
    setItems([...items, {
      name: "",
      quantity: 1,
      unit: "szt.",
      net_price: 0,
      vat_rate: 23,
    }]);
  };

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const updateItem = (index: number, field: string, value: any) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };
    setItems(newItems);
    setValue("items", newItems);
  };

  const calculateTotals = () => {
    let netTotal = 0;
    let vatTotal = 0;

    items.forEach(item => {
      if (item.name && item.quantity && item.net_price) {
        const netAmount = item.quantity * item.net_price;
        const vatAmount = netAmount * (item.vat_rate / 100);
        netTotal += netAmount;
        vatTotal += vatAmount;
      }
    });

    return {
      net: netTotal.toFixed(2),
      vat: vatTotal.toFixed(2),
      gross: (netTotal + vatTotal).toFixed(2),
    };
  };

  const totals = calculateTotals();

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Nowa faktura</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Company selection */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Dane firmy</h2>
          <div>
            <label className="block text-sm font-medium mb-2">Firma</label>
            <select
              {...register("company_id")}
              className="w-full p-2 border rounded-md"
            >
              <option value="">Wybierz firmę</option>
              {companies?.map((company: any) => (
                <option key={company.id} value={company.id}>
                  {company.name} (NIP: {company.nip})
                </option>
              ))}
            </select>
            {errors.company_id && (
              <p className="text-red-500 text-sm mt-1">{errors.company_id.message}</p>
            )}
          </div>
        </div>

        {/* Invoice details */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Dane faktury</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Numer faktury</label>
              <input
                {...register("invoice_number")}
                type="text"
                className="w-full p-2 border rounded-md"
                placeholder="FV/2024/01/001"
              />
              {errors.invoice_number && (
                <p className="text-red-500 text-sm mt-1">{errors.invoice_number.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Metoda płatności</label>
              <select
                {...register("payment_method")}
                className="w-full p-2 border rounded-md"
              >
                <option value="transfer">Przelew</option>
                <option value="cash">Gotówka</option>
                <option value="card">Karta</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Data wystawienia</label>
              <input
                {...register("issue_date")}
                type="date"
                className="w-full p-2 border rounded-md"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Data sprzedaży</label>
              <input
                {...register("sale_date")}
                type="date"
                className="w-full p-2 border rounded-md"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Termin płatności</label>
              <input
                {...register("due_date")}
                type="date"
                className="w-full p-2 border rounded-md"
              />
            </div>
          </div>
        </div>

        {/* Contractor data */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Dane kontrahenta</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">NIP</label>
              <input
                {...register("contractor_data.nip")}
                type="text"
                className="w-full p-2 border rounded-md"
                placeholder="1234567890"
              />
              {errors.contractor_data?.nip && (
                <p className="text-red-500 text-sm mt-1">{errors.contractor_data.nip.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Nazwa</label>
              <input
                {...register("contractor_data.name")}
                type="text"
                className="w-full p-2 border rounded-md"
                placeholder="Nazwa firmy"
              />
              {errors.contractor_data?.name && (
                <p className="text-red-500 text-sm mt-1">{errors.contractor_data.name.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Ulica</label>
              <input
                {...register("contractor_data.address.street")}
                type="text"
                className="w-full p-2 border rounded-md"
                placeholder="ul. Przykładowa 1"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Miasto</label>
              <input
                {...register("contractor_data.address.city")}
                type="text"
                className="w-full p-2 border rounded-md"
                placeholder="Warszawa"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Kod pocztowy</label>
              <input
                {...register("contractor_data.address.postal_code")}
                type="text"
                className="w-full p-2 border rounded-md"
                placeholder="00-001"
              />
            </div>
          </div>
        </div>

        {/* Invoice items */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Pozycje faktury</h2>
            <button
              type="button"
              onClick={addItem}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            >
              <Plus size={16} />
              Dodaj pozycję
            </button>
          </div>

          <div className="space-y-3">
            {items.map((item, index) => (
              <div key={index} className="flex gap-3 items-end">
                <div className="flex-1">
                  <label className="block text-sm font-medium mb-1">Nazwa</label>
                  <input
                    type="text"
                    value={item.name}
                    onChange={(e) => updateItem(index, "name", e.target.value)}
                    className="w-full p-2 border rounded-md"
                    placeholder="Nazwa produktu/usługi"
                  />
                </div>

                <div className="w-24">
                  <label className="block text-sm font-medium mb-1">Ilość</label>
                  <input
                    type="number"
                    step="0.01"
                    value={item.quantity}
                    onChange={(e) => updateItem(index, "quantity", parseFloat(e.target.value))}
                    className="w-full p-2 border rounded-md"
                  />
                </div>

                <div className="w-20">
                  <label className="block text-sm font-medium mb-1">Jedn.</label>
                  <input
                    type="text"
                    value={item.unit}
                    onChange={(e) => updateItem(index, "unit", e.target.value)}
                    className="w-full p-2 border rounded-md"
                  />
                </div>

                <div className="w-32">
                  <label className="block text-sm font-medium mb-1">Cena netto</label>
                  <input
                    type="number"
                    step="0.01"
                    value={item.net_price}
                    onChange={(e) => updateItem(index, "net_price", parseFloat(e.target.value))}
                    className="w-full p-2 border rounded-md"
                  />
                </div>

                <div className="w-24">
                  <label className="block text-sm font-medium mb-1">VAT %</label>
                  <select
                    value={item.vat_rate}
                    onChange={(e) => updateItem(index, "vat_rate", parseInt(e.target.value))}
                    className="w-full p-2 border rounded-md"
                  >
                    <option value={23}>23%</option>
                    <option value={8}>8%</option>
                    <option value={5}>5%</option>
                    <option value={0}>0%</option>
                  </select>
                </div>

                <button
                  type="button"
                  onClick={() => removeItem(index)}
                  className="p-2 text-red-500 hover:bg-red-50 rounded-md"
                >
                  <Trash2 size={20} />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Totals */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Podsumowanie</h2>
          <div className="space-y-2 text-right">
            <div className="flex justify-between">
              <span>Wartość netto:</span>
              <span className="font-medium">{totals.net} PLN</span>
            </div>
            <div className="flex justify-between">
              <span>Podatek VAT:</span>
              <span className="font-medium">{totals.vat} PLN</span>
            </div>
            <div className="flex justify-between text-lg font-bold">
              <span>Wartość brutto:</span>
              <span>{totals.gross} PLN</span>
            </div>
          </div>
        </div>

        {/* Submit buttons */}
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={createInvoiceMutation.isPending}
            className="px-6 py-3 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50"
          >
            {createInvoiceMutation.isPending ? "Tworzenie..." : "Utwórz i wyślij do KSeF"}
          </button>
          <button
            type="button"
            onClick={() => router.push("/invoices")}
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          >
            Anuluj
          </button>
        </div>
      </form>
    </div>
  );
}