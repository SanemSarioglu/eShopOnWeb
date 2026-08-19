using System.Collections.Immutable;
using System.Linq;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Diagnostics;

namespace EfCoreSqlAnalyzer
{
    [DiagnosticAnalyzer(LanguageNames.CSharp)]
    public class EfCoreRawSqlAnalyzer : DiagnosticAnalyzer
    {
        public const string DiagnosticId = "EFSQL001";

        private static readonly string[] TargetMethodNames =
        {
            "FromSqlRaw",
            "SqlQueryRaw",
            "ExecuteSqlRaw",
            "ExecuteSqlRawAsync",
        };

        private static readonly DiagnosticDescriptor Rule = new DiagnosticDescriptor(
            id: DiagnosticId,
            title: "Non-literal string passed to an EF Core raw-SQL API",
            messageFormat:
                "Non-literal string passed to '{0}'. If this string is built from concatenation or " +
                "interpolation of external input, this is SQL injection. Use FromSqlInterpolated or a " +
                "parameterized query instead.",
            category: "Security",
            defaultSeverity: DiagnosticSeverity.Error,
            isEnabledByDefault: true,
            description: "Non-literal string passed to an EF Core raw-SQL API (FromSqlRaw / SqlQueryRaw / " +
                          "ExecuteSqlRaw / ExecuteSqlRawAsync).",
            helpLinkUri: "https://learn.microsoft.com/ef/core/querying/sql-queries#passing-parameters");

        public override ImmutableArray<DiagnosticDescriptor> SupportedDiagnostics =>
            ImmutableArray.Create(Rule);

        public override void Initialize(AnalysisContext context)
        {
            context.ConfigureGeneratedCodeAnalysis(GeneratedCodeAnalysisFlags.None);
            context.EnableConcurrentExecution();
            context.RegisterSyntaxNodeAction(AnalyzeInvocation, SyntaxKind.InvocationExpression);
        }

        private static void AnalyzeInvocation(SyntaxNodeAnalysisContext context)
        {
            var invocation = (InvocationExpressionSyntax)context.Node;

            if (invocation.Expression is not MemberAccessExpressionSyntax memberAccess)
                return;

            string methodName = memberAccess.Name.Identifier.Text;
            if (!TargetMethodNames.Contains(methodName))
                return;

            var arguments = invocation.ArgumentList.Arguments;
            if (arguments.Count == 0)
                return;

            ExpressionSyntax sqlArgument = arguments[0].Expression;

            if (IsStringLiteral(sqlArgument))
                return;

            var diagnostic = Diagnostic.Create(Rule, invocation.GetLocation(), methodName);
            context.ReportDiagnostic(diagnostic);
        }

        private static bool IsStringLiteral(ExpressionSyntax expression)
        {
            return expression is LiteralExpressionSyntax literal
                   && literal.IsKind(SyntaxKind.StringLiteralExpression);
        }
    }
}
