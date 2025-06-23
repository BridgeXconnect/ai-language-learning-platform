"use client"
import { useState, useMemo } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ArrowUpDown, Search } from "lucide-react"
import type { ColumnDefinition } from "@/lib/types"
import { Skeleton } from "@/components/ui/skeleton"

interface DataTableProps<T> {
  columns: ColumnDefinition<T>[]
  data: T[]
  isLoading?: boolean
  searchColumn?: keyof T | string // Column to search on
  searchPlaceholder?: string
  itemsPerPageOptions?: number[]
}

// Helper to get nested property value
const getNestedValue = (obj: any, path: string): any => {
  return path.split(".").reduce((acc, part) => acc && acc[part], obj)
}

export function DataTable<T extends { id: string | number }>({
  columns,
  data,
  isLoading = false,
  searchColumn,
  searchPlaceholder = "Search...",
  itemsPerPageOptions = [10, 20, 50, 100],
}: DataTableProps<T>) {
  const [searchTerm, setSearchTerm] = useState("")
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage, setItemsPerPage] = useState(itemsPerPageOptions[0])
  const [sortConfig, setSortConfig] = useState<{ key: keyof T | string; direction: "asc" | "desc" } | null>(null)

  const filteredData = useMemo(() => {
    let filtered = data
    if (searchTerm && searchColumn) {
      filtered = filtered.filter((item) => {
        const value = getNestedValue(item, searchColumn as string)
        return String(value).toLowerCase().includes(searchTerm.toLowerCase())
      })
    }
    return filtered
  }, [data, searchTerm, searchColumn])

  const sortedData = useMemo(() => {
    const sortableItems = [...filteredData]
    if (sortConfig !== null) {
      sortableItems.sort((a, b) => {
        const valA = getNestedValue(a, sortConfig.key as string)
        const valB = getNestedValue(b, sortConfig.key as string)

        if (valA < valB) {
          return sortConfig.direction === "asc" ? -1 : 1
        }
        if (valA > valB) {
          return sortConfig.direction === "asc" ? 1 : -1
        }
        return 0
      })
    }
    return sortableItems
  }, [filteredData, sortConfig])

  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage
    return sortedData.slice(startIndex, startIndex + itemsPerPage)
  }, [sortedData, currentPage, itemsPerPage])

  const totalPages = Math.ceil(sortedData.length / itemsPerPage)

  const requestSort = (key: keyof T | string) => {
    let direction: "asc" | "desc" = "asc"
    if (sortConfig && sortConfig.key === key && sortConfig.direction === "asc") {
      direction = "desc"
    }
    setSortConfig({ key, direction })
  }

  const renderTableContent = () => {
    if (isLoading) {
      return Array(itemsPerPage)
        .fill(0)
        .map((_, rowIndex) => (
          <TableRow key={`skeleton-${rowIndex}`}>
            {columns.map((col, colIndex) => (
              <TableCell key={`skeleton-cell-${rowIndex}-${colIndex}`}>
                <Skeleton className="h-6 w-full" />
              </TableCell>
            ))}
          </TableRow>
        ))
    }
    if (paginatedData.length === 0) {
      return (
        <TableRow>
          <TableCell colSpan={columns.length} className="h-24 text-center">
            No results found.
          </TableCell>
        </TableRow>
      )
    }
    return paginatedData.map((row) => (
      <TableRow key={row.id}>
        {columns.map((col) => (
          <TableCell key={String(col.accessorKey)}>
            {col.cell
              ? col.cell({ row, value: getNestedValue(row, col.accessorKey as string) })
              : String(getNestedValue(row, col.accessorKey as string) ?? "")}
          </TableCell>
        ))}
      </TableRow>
    ))
  }

  return (
    <div className="space-y-4">
      {searchColumn && (
        <div className="flex items-center py-4">
          <div className="relative w-full max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder={searchPlaceholder}
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              className="pl-10"
            />
          </div>
        </div>
      )}
      <div className="rounded-md border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              {columns.map((col) => (
                <TableHead key={String(col.accessorKey)}>
                  {col.enableSorting ? (
                    <Button variant="ghost" onClick={() => requestSort(col.accessorKey)}>
                      {typeof col.header === "function" ? col.header() : col.header}
                      <ArrowUpDown className="ml-2 h-4 w-4" />
                    </Button>
                  ) : typeof col.header === "function" ? (
                    col.header()
                  ) : (
                    col.header
                  )}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>{renderTableContent()}</TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-between py-4">
        <div className="text-sm text-muted-foreground">
          Showing {Math.min((currentPage - 1) * itemsPerPage + 1, sortedData.length)} to{" "}
          {Math.min(currentPage * itemsPerPage, sortedData.length)} of {sortedData.length} entries
        </div>
        <div className="flex items-center space-x-2">
          <Select value={String(itemsPerPage)} onValueChange={(value) => setItemsPerPage(Number(value))}>
            <SelectTrigger className="w-[70px]">
              <SelectValue placeholder={itemsPerPage} />
            </SelectTrigger>
            <SelectContent>
              {itemsPerPageOptions.map((option) => (
                <SelectItem key={option} value={String(option)}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
          >
            Previous
          </Button>
          <span className="text-sm">
            Page {currentPage} of {totalPages > 0 ? totalPages : 1}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
            disabled={currentPage === totalPages || totalPages === 0}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  )
}
