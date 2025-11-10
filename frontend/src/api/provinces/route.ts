import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
    const searchParams = request.nextUrl.searchParams;
    const provinceName = searchParams.get('province');

    try {
        let apiUrl = 'https://vietnamlabs.com/api/vietnamprovince';
        
        // Nếu có tên tỉnh, lấy wards của tỉnh đó
        if (provinceName) {
            apiUrl += `?province=${encodeURIComponent(provinceName)}`;
        }

        const response = await fetch(apiUrl, {
            headers: {
                'Content-Type': 'application/json',
            },
            // Add cache to reduce requests
            next: { revalidate: 3600 } // Cache for 1 hour
        });

        if (!response.ok) {
            throw new Error('Failed to fetch data');
        }

        const data = await response.json();
        
        return NextResponse.json(data);
    } catch (error) {
        console.error('Error fetching provinces:', error);
        return NextResponse.json(
            { error: 'Failed to fetch data' },
            { status: 500 }
        );
    }
}
