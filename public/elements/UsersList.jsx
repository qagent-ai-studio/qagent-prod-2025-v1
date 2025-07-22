import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { User, Calendar } from "lucide-react"

export default function UsersList() {
    // Función para obtener la clase de color según el rol
    const getRoleBadgeVariant = (role) => {
        role = role ? role.toLowerCase() : "";
        switch (role) {
            case "admin":
                return "destructive";
            case "analista":
                return "secondary";
            default:
                return "outline";
        }
    };

    return (
        <div className="w-full overflow-auto rounded-md border">
            <Table>
                <TableCaption>Listado de usuarios registrados en la plataforma</TableCaption>
                <TableHeader>
                    <TableRow>
                        <TableHead className="w-[250px]">Email</TableHead>
                        <TableHead className="w-[150px]">Rol</TableHead>
                        <TableHead className="text-right">Fecha de Registro</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {props.users && props.users.length > 0 ? (
                        props.users.map((user, index) => (
                            <TableRow key={index}>
                                <TableCell className="font-medium">
                                    <div className="flex items-center gap-2">
                                        <User className="h-4 w-4 opacity-70" />
                                        {user.email}
                                    </div>
                                </TableCell>
                                <TableCell>
                                    <Badge variant={getRoleBadgeVariant(user.role)}>
                                        {user.role || "Usuario"}
                                    </Badge>
                                </TableCell>
                                <TableCell className="text-right">
                                    <div className="flex items-center justify-end gap-2">
                                        <Calendar className="h-4 w-4 opacity-70" />
                                        {user.created_at || "Desconocida"}
                                    </div>
                                </TableCell>
                            </TableRow>
                        ))
                    ) : (
                        <TableRow>
                            <TableCell colSpan={3} className="text-center py-4">
                                No hay usuarios registrados
                            </TableCell>
                        </TableRow>
                    )}
                </TableBody>
            </Table>
        </div>
    );
} 