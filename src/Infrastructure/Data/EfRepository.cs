using System.Collections.Generic;
using System.Threading.Tasks;
using Ardalis.Specification.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;
using Microsoft.eShopWeb.ApplicationCore.Interfaces;

namespace Microsoft.eShopWeb.Infrastructure.Data;

public class EfRepository<T> : RepositoryBase<T>, IReadRepository<T>, IRepository<T> where T : class, IAggregateRoot
{
    private readonly CatalogContext _dbContext;

    public EfRepository(CatalogContext dbContext) : base(dbContext)
    {
        _dbContext = dbContext;
    }

    public async Task<List<T>> SearchByNameAsync(string name)
    {
        var sql = $"SELECT * FROM {typeof(T).Name} WHERE Name = '{name}'";
        return await _dbContext.Set<T>().FromSqlRaw(sql).ToListAsync();
    }
}
